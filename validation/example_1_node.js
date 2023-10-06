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


const cleanupGDriveFolder = async (folderName) => {
  const driveService = google.drive({ version: 'v3', auth: jwtClient });
  try {
    const folderIdRes = await driveService.files.list({
      q: `name='${folderName}' and mimeType='application/vnd.google-apps.folder'`,
      fields: 'files(id)',
    });
    const folderId = folderIdRes.data.files[0].id;

    const filesRes = await driveService.files.list({
      q: `'${folderId}' in parents`,
      fields: 'files(id)',
    });
    const files = filesRes.data.files;

    for (const file of files) {
      await driveService.files.delete({
        fileId: file.id,
      });
    }
    console.log('Folder cleaned up successfully.');
  } catch (error) {
    console.error('Error cleaning up folder:', error.message);
  }
};


async function downloadFile(fileName, folderName) {
  const driveService = google.drive({ version: 'v3', auth: jwtClient });
  try {
      // Step 1: Find the file ID
      const folderResults = await driveService.files.list({
          q: `name='${folderName}' and mimeType='application/vnd.google-apps.folder'`,
          fields: "files(id)"
      });
      const folders = folderResults.data.files;
      if (!folders || folders.length === 0) {
          console.error(`Folder ${folderName} not found.`);
          return;
      }
      const folderId = folders[0].id;
      
      const fileResults = await driveService.files.list({
          q: `name='${fileName}' and '${folderId}' in parents`,
          fields: "files(id)"
      });
      const files = fileResults.data.files;
      if (!files || files.length === 0) {
          console.error(`File ${fileName} not found in folder ${folderName}.`);
          return;
      }
      const fileId = files[0].id;
      
      // Step 2: Download the file
      const dest = fs.createWriteStream(path.join(downloadPath, fileName));
      const res = await driveService.files.get({
          fileId: fileId,
          alt: 'media'
      }, {
          responseType: 'stream'
      });
      
      res.data
          .on('end', () => {
              console.log(`File ${fileName} downloaded successfully.`);
          })
          .on('error', err => {
              console.error('Error downloading file:', err);
              dest.close();
          })
          .pipe(dest);
      
  } catch (error) {
      console.error('Error:', error.message);
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
              downloadFile(fileName, folderName);
            } catch (error) {
              console.error('Error in export: ' + e);  
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
