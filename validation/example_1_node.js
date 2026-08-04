/*
Author: Sofia Ermida (sofia.ermida@ipma.pt; @ermida_sofia)

This code is free and open. 
By using this code and any data derived with it, 
you agree to cite the following reference 
in any publications derived from them:
Ermida, S.L., Soares, P., Mantas, V., Göttsche, F.-M., Trigo, I.F., 2020. 
    Google Earth Engine open-source code for Land Surface Temperature estimation from the Landsat series.
    Remote Sensing, 12 (9), 1471; https://doi.org/10.3390/rs12091471

Example 1:
  This example shows how to compute Landsat LST from Landsat-8 over Coimbra
  This corresponds to the example images shown in Ermida et al. (2020)
    
*/


// Require necessary modules
const ee = require('@google/earthengine');
const privateKey = require('./.gee-sa-priv-key.json');
const {google} = require('googleapis');
const drive = google.drive('v3');
const fs = require('fs');
const path = require('path');

// Script variables
const folderName = 'node_lst_geotiffs';
const downloadPath = '/app/downloads';

const jwtClient = new google.auth.JWT(
  privateKey.client_email,
  null,
  privateKey.private_key,
  ['https://www.googleapis.com/auth/drive'],
  null
);


// Drive allows several folders to share a name, and files.list does not
// guarantee a stable order. The 8 exports here run concurrently and each does
// find-or-create on `folderName`, so more than one folder with that name can
// exist. Resolving the name separately per download - as this file used to -
// could therefore land on a different folder each time, which is why a random
// subset of bands came back "not found" and why retrying never helped: the
// file was never going to be in the folder being searched.
//
// So: resolve every folder with the name, once, and treat them as one space.
let cachedFolderIds = null;

const resolveFolderIds = async (driveService, folderName) => {
  if (cachedFolderIds) return cachedFolderIds;
  const res = await driveService.files.list({
    q:
      `name='${folderName}' and trashed=false and ` +
      `mimeType='application/vnd.google-apps.folder'`,
    fields: 'files(id,name,createdTime)',
  });
  const folders = res.data.files || [];
  if (folders.length === 0) {
    console.error(`Folder ${folderName} not found.`);
  } else if (folders.length > 1) {
    console.warn(
      `WARNING: ${folders.length} folders are named '${folderName}'. ` +
      `Searching all of them. IDs: ` +
      folders.map((f) => `${f.id} (created ${f.createdTime})`).join(', ')
    );
  } else {
    console.log(`Folder ${folderName} resolved to ${folders[0].id}.`);
  }
  cachedFolderIds = folders.map((f) => f.id);
  return cachedFolderIds;
};

const parentClause = (folderIds) =>
  '(' + folderIds.map((id) => `'${id}' in parents`).join(' or ') + ')';

const cleanupGDriveFolder = async (folderName) => {
  const driveService = google.drive({ version: 'v3', auth: jwtClient });
  try {
    const folderIds = await resolveFolderIds(driveService, folderName);
    if (folderIds.length === 0) return;

    // Clean every matching folder. Leaving stale files in a duplicate would
    // let a later run download the previous run's output and compare it as if
    // it were fresh - a false pass.
    const filesRes = await driveService.files.list({
      q: `${parentClause(folderIds)} and trashed=false`,
      fields: 'files(id,name)',
    });
    const files = filesRes.data.files || [];

    for (const file of files) {
      await driveService.files.delete({
        fileId: file.id,
      });
    }
    console.log(
      `Folder cleaned up successfully (${files.length} file(s) removed ` +
      `from ${folderIds.length} folder(s) named '${folderName}').`
    );
    // The cached IDs stay valid: cleanup removes files, not the folders.
  } catch (error) {
    console.error('Error cleaning up folder:', error.message);
  }
};


const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

// Retained as a genuine (if secondary) effect: Drive can take a moment to make
// a just-exported file listable. The retry is cheap when it is not needed.
const FILE_LOOKUP_ATTEMPTS = 12;
const FILE_LOOKUP_DELAY_MS = 10000;

// Earth Engine splits a large export into tiles named like
// "TCWV-0000000000-0000000000.tif" instead of "TCWV.tif". An exact-name lookup
// would never find those, so match the prefix and report what turned up.
async function findFileId(driveService, fileName, folderIds, folderName) {
  const stem = fileName.replace(/\.tif$/, '');
  const scope = parentClause(folderIds);
  for (let attempt = 1; attempt <= FILE_LOOKUP_ATTEMPTS; attempt++) {
      const exact = await driveService.files.list({
          q: `name='${fileName}' and ${scope} and trashed=false`,
          fields: "files(id,name)"
      });
      const files = exact.data.files;
      if (files && files.length > 0) {
          if (attempt > 1) {
              console.log(`${fileName} appeared in Drive after ${attempt} lookups.`);
          }
          return files[0].id;
      }

      const prefixed = await driveService.files.list({
          q: `name contains '${stem}' and ${scope} and trashed=false`,
          fields: "files(id,name)"
      });
      const near = prefixed.data.files || [];
      if (near.length > 0) {
          console.warn(
            `${fileName} is not present under that exact name, but ` +
            `${near.length} file(s) match the prefix: ` +
            near.map((f) => f.name).join(', ') +
            '. Earth Engine may have tiled this export.'
          );
          return near[0].id;
      }

      if (attempt < FILE_LOOKUP_ATTEMPTS) {
          console.log(
            `${fileName} not listable in ${folderName} yet ` +
            `(lookup ${attempt}/${FILE_LOOKUP_ATTEMPTS}); retrying in ` +
            `${FILE_LOOKUP_DELAY_MS / 1000}s`
          );
          await sleep(FILE_LOOKUP_DELAY_MS);
      }
  }
  return null;
}

async function downloadFile(fileName, folderName) {
  const driveService = google.drive({ version: 'v3', auth: jwtClient });
  try {
      // Step 1: Find the file ID
      const folderIds = await resolveFolderIds(driveService, folderName);
      if (folderIds.length === 0) return false;

      const fileId = await findFileId(driveService, fileName, folderIds, folderName);
      if (!fileId) {
          console.error(
            `File ${fileName} not found in folder ${folderName} after ` +
            `${FILE_LOOKUP_ATTEMPTS} lookups over ` +
            `${(FILE_LOOKUP_ATTEMPTS * FILE_LOOKUP_DELAY_MS) / 1000}s.`
          );
          // Say what IS there, so the next failure is diagnosable from the log
          // rather than needing another instrumented run.
          try {
              const listing = await driveService.files.list({
                  q: `${parentClause(folderIds)} and trashed=false`,
                  fields: "files(name)"
              });
              const names = (listing.data.files || []).map((f) => f.name);
              console.error(
                `  Folder actually contains ${names.length} file(s): ` +
                (names.length ? names.sort().join(', ') : '(empty)')
              );
          } catch (listErr) {
              console.error('  Could not list folder contents:', listErr.message);
          }
          return false;
      }

      // Step 2: Download the file
      const dest = fs.createWriteStream(path.join(downloadPath, fileName));
      const res = await driveService.files.get({
          fileId: fileId,
          alt: 'media'
      }, {
          responseType: 'stream'
      });

      // Wait for the write stream to finish, not just the read stream to end.
      // Returning early left the process free to exit mid-write.
      await new Promise((resolve, reject) => {
          dest.on('finish', resolve);
          dest.on('error', reject);
          res.data.on('error', reject);
          res.data.pipe(dest);
      });

      console.log(`File ${fileName} downloaded successfully.`);
      return true;

  } catch (error) {
      console.error(`Error downloading ${fileName}:`, error.message);
      return false;
  }
}


const logTaskStatusAsync = (taskId, description) => {
  return new Promise((resolve, reject) => {
      const logStatus = async () => {
          try {
              const statusRes = await ee.data.getTaskStatus(taskId);
              const status = statusRes[0].state;
              console.log(description, 'status:', status);
              if (status === 'COMPLETED') {
                  resolve('Task completed');
              } else if (status === 'FAILED') {
                  reject(new Error('Task failed'));
              } else {
                  setTimeout(logStatus, 30000);  // Check again in 30 seconds
              }
          } catch (error) {
              reject(error);
          }
      };
      logStatus();
  });
};


// Function to convert Kelvin to Celsius
function kelvinToCelsius(image) {
  return image.subtract(273.15);
}


// Initialize Earth Engine with the service account
ee.data.authenticateViaPrivateKey(privateKey, () => {
    ee.initialize();

    // Your GEE code starts here
    const geometry = ee.Geometry.Rectangle([-8.91, 40.0, -8.3, 40.4]);
    const satellite = 'L8';
    const date_start = '2022-05-15';
    const date_end = '2022-05-31';
    const use_ndvi = true;

    // Assuming LandsatLST.collection is a function you've defined elsewhere
    const LandsatLST = require('./modules/Landsat_LST');
    const LandsatColl = LandsatLST.collection(satellite, date_start, date_end, geometry, use_ndvi);

    // select the first feature
    var exImage = LandsatColl.first();

    var cmap1 = ['blue', 'cyan', 'green', 'yellow', 'red'];
    var cmap2 = ['F2F2F2','EFC2B3','ECB176','E9BD3A','E6E600','63C600','00A600']; 

    // Visualization parameters for each layer
    const visualizations = [
      {bands: ['TPW'], min: 0.0, max: 60.0, palette: cmap1, description: 'TCWV'},
      {bands: ['TPWpos'], min: 0.0, max: 9.0, palette: cmap1, description: 'TCWVpos'},
      {bands: ['FVC'], min: 0.0, max: 1.0, palette: cmap2, description: 'FVC'},
      {bands: ['EM'], min: 0.9, max: 1.0, palette: cmap1, description: 'Emissivity'},
      {bands: ['B10'], min: 290, max: 320, palette: cmap1, description: 'TIR_BT'},
      {bands: ['LST'], min: 290, max: 320, palette: cmap1, description: 'LST'},
      {bands: ['LST'], description: 'LST_Celsius_Raw'},
      {bands: ['SR_B4', 'SR_B3', 'SR_B2'], min: 0, max: 0.3, description: 'RGB'}
    ];

    // Call the cleanup function before starting the export process
    cleanupGDriveFolder(folderName).then(() => {    
      // Convert each layer to an RGB image and export
      visualizations.forEach((vis) => {
        let exportImage;
        let imageDescription;
    
        if (vis.description === 'RGB') {
          // Special case for RGB. We don't need to apply a palette.
          exportImage = exImage.select(vis.bands);
        } else if (vis.description === 'LST_Celsius_Raw') {
          // Special case for raw LST in Celsius.
          // Assuming kelvinToCelsius is a function you've defined elsewhere
          exportImage = kelvinToCelsius(exImage.select(vis.bands));
        } else {
          exportImage = exImage.visualize({
            bands: vis.bands,
            min: vis.min,
            max: vis.max,
            palette: vis.palette
          });
        }
    
        const exportTask = ee.batch.Export.image.toDrive({
          image: exportImage,
          description: vis.description,
          scale: 30,
          region: geometry,
          fileFormat: 'GeoTIFF',
          folder: folderName,
          crs: 'EPSG:4326',
          formatOptions: {
            cloudOptimized: true
          },
          fileNamePrefix: vis.description
        });

        exportTask.start(
          async function() {
            console.log(vis.description + ' export started!');
            try {
              await logTaskStatusAsync(exportTask.id, vis.description);  // Log the status of this task periodically
              console.log(vis.description + ' export completed!');
              const fileName = vis.description + '.tif';
              // Awaited: previously this was fire-and-forget, so a failed
              // download was a log line the job never noticed.
              const downloaded = await downloadFile(fileName, folderName);
              if (!downloaded) {
                console.error('Download failed for ' + vis.description);
                process.exitCode = 1;
              }
            } catch (error) {
              // The binding is `error`; referencing `e` here threw
              // ReferenceError from inside the handler, so the real failure was
              // never printed and the process died on the error path instead.
              console.error(
                'Error in export of ' + vis.description + ': ' + error
              );
              process.exitCode = 1;
            }
          }
        );
      });
    }).catch((error) => {
      console.error('Error:', error);
    });
}, (err) => {
    console.error('Authentication error: ' + err);
});
