#!/bin/bash

# Function to modify the file
modify_file () {
    # Define the file path
    FILE_PATH="/app/modules/$1"

    # Backup the original file
    cp $FILE_PATH "$FILE_PATH.bak"

    # Modify the require paths
    sed -i 's|users/sofiaermida/landsat_smw_lst:modules/|/app/modules/|g' $FILE_PATH

    # Add NodeJS related code
    grep -q "NodeJS related" $FILE_PATH || sed -i '1s|^|// NodeJS related ----------------------------------------------------------------\n// Require necessary modules\nconst ee = require('"'"'@google/earthengine'"'"');\nconst privateKey = require('"'"'../.gee-sa-priv-key.json'"'"');\n// -------------------------------------------------------------------------------\n\n|' $FILE_PATH

    echo "Modifications completed for $1."
}

# Call the function for each file
modify_file "Landsat_LST.js"
modify_file "ASTER_bare_emiss.js"
modify_file "broadband_emiss.js"
modify_file "compute_emissivity.js"
modify_file "compute_NDVI.js"
modify_file "NCEP_TPW.js"
modify_file "SMW_coefficients.js"
modify_file "SMWalgorithm.js"