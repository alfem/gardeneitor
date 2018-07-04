


function programSave() {
 var f=$('#programForm');

 $.ajax({
  type: 'POST',
  url: 'program-save',
  data: f.serialize(),
   success: function(msg){ swal({
            title: "SAVED",
            text: "Program stored and scheduled",
            type: "info"
        }); }
   });
}

function programRun() {
    console.log("Runnning Program Now");
    var url = "program-run"; 
    callApi(url);
}

function programSwitch(status) {
    console.log("Runnning Program Now");
    var url = "program-switch/"; 
    url += status ? "1" : "0";
    callApi(url);
}


function setPump(status) {
    console.log("Executing setPump");
    var url = "pump/"; 
    url += status ? "1" : "0";
    callApi(url);
}

function setRelay(relay, status) {
    console.log("Executing setRelay");
    var url = "valve/"; 
    url += relay +"/";
    url += status ? '1' : '0';
    callApi(url);
}


function setAll(status) {
    console.log("Executing setAll");
    var url = status ? 'all_on/' : 'all_off/';
    callApi(url);
}



function callApi(url) {
    console.log("Executing callApi");
    $.get(url, function () {
        console.log("Sent request to server");
    }).done(function () {
        console.log("Completed request");
    }).fail(function () {
        console.error("Relay status failure");
        swal({
            title: "Gardeneitor",
            text: "Server returned an error",
            type: "error"
        });
    });
}
function status() {
    console.log("Executing status");

    $.get("log/", function () {
        console.log("Sent request to server");
    }).done(function (res) {
        console.log("Completed request");
        $(logbox).text(res);
    }).fail(function () {
        console.error("Status failure");
        swal({
            title: "Gardeneitor",
            text: "Server returned an error",
            type: "error"
        });
    });


}

function getRelayStatus(relay) {
    console.log("Executing getRelayStatus");
    $.get('status/' + relay, function () {
        console.log("Sent request to server");
    }).done(function (res) {
        console.log("Completed request");
        var msg = (parseInt(res) > 0) ? "ON" : "OFF"
        msg = "Relay " + relay + " is " + msg;
        swal(msg);
    }).fail(function () {
        console.error("Relay status failure");
        swal({
            title: "Gardeneitor",
            text: "Server returned an error",
            type: "error"
        });
    });
}
