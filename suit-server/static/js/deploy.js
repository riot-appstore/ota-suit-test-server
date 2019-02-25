/*
 * Copyright (C) 2017-2018 Hendrik van Essen and FU Berlin
 *
 * This file is subject to the terms and conditions of the GNU Lesser
 * General Public License v2.1. See the file LICENSE in the top level
 * directory for more details.
*/

//$(window).on("load", function() {
//
//    document.getElementById('fileid').addEventListener('change', sign_manifest);
//
//});
//

//function openDialog() {
//    return document.getElementById('fileid').click();
//}

function deploy_app(target_addr) {

	document.getElementById('fileid').addEventListener('change', function() {
		var reader = new FileReader();
		reader.onload = function() {

			var arrayBuffer = this.result;
			array = new Uint8Array(arrayBuffer);

            get_manifest(target_addr, array);

		}
		reader.readAsArrayBuffer(this.files[0]);
	}, false);

//    function get_key() {
//        var key = document.getElementById('fileid').files[0];
//        new fr = FileReader();
//        console.log("got key, type is: " + typeof(key));
//        console.log("key is: " + key);
//    }
    document.getElementById('fileid').click();
}

function get_manifest(target_addr, key) {

    var xhttp = new XMLHttpRequest();

    console.log("target address is : " + target_addr);
    
    xhttp.onreadystatechange = function() {

        if (this.readyState === 4 ) {

            var unsigned_manifest = null;
            try {
                console.log("response is: " + this.response);
                unsigned_manifest = this.response;
            }
            catch(e) {
                alert("Server sent bad manifest");
                return;
            }

            // ask for the key
            enc = new TextEncoder();
            var unsigned_manifest_bstr = Buffer.from(unsigned_manifest, 'base64').toString('binary');
            var len = unsigned_manifest_bstr.length;
            console.log("unsigned manifest binary string length is: " + len);
            var unsigned_manifest_array = new Uint8Array(len);
            for (var i = 0; i < len; i++)        {
                unsigned_manifest_array[i] = unsigned_manifest_bstr.charCodeAt(i);
            }
            //arguments are both a uint8 array
            signed_manifest = nacl.sign(unsigned_manifest_array, key);
            upload_manifest(signed_manifest, target_addr);
       }
    };


    xhttp.open("GET", "/get_manifest?app_name=suit_updater", true);
   // xhttp.setRequestHeader("enctype", "multipart/form-data");

    xhttp.send();
}

            


function upload_manifest(signed_manifest, target_addr) {

    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4) {

            deploy_manifest(target_addr);
        }
    }

    xhttp.open("POST", "/upload_signed_manifest", true);
 //   xhttp.setRequestHeader("Content-type", "multipart/form-data");
    var formData = new FormData();
    var manifest_file = new File(signed_manifest, "my_manifest");
  //  binaryString = String.fromCharCode.apply(null, array);
    formData.append('signed_manifest', manifest_file);
    xhttp.send(formData);
}

function deploy_manifest(target_addr) {

    var xhttp = new XMLHttpRequest();

    xhttp.open("POST", "/ota_deploy", true);
  //  xhttp.setRequestHeader("Content-type", "multipart/form-data");
    var formData = new FormData();
    formData.append('target', target_addr);
    xhttp.send(formData);
}
