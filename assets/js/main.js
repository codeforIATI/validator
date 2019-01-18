/*
 * Main Javascript file for iati_validator.
 *
 * This file bundles all of your javascript together using webpack.
 */

// JavaScript modules
require('jquery');
require('font-awesome-webpack');
require('popper.js');
require('bootstrap');
require('bs-custom-file-input').init();

// Your own code
require('./plugins.js');
require('./script.js');
