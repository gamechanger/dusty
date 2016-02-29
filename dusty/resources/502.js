var consumeInterval;
var upInterval;

$(document).ready(function() {
    registerConsumer(function(appName, consumerId) {
        $('#title').append(appName);
        consumeInterval = window.setInterval(consumeLogs, 1000, consumerId);
        upInterval = window.setInterval(checkServiceAvailability, 1000, consumerId);
    });
});

var getPort = function() {
  if(location.port != ''){
      return location.port;
  }
  else if(location.protocol== 'http:'){
     return 80;
  }
  else if(location.protocol== 'https:'){
     return 443;
  }
};

var registerConsumer = function(cb) {
    $.post(
        'http://127.0.0.1:60912/register-consumer',
        {
            hostname: location.hostname,
            port: getPort()
        },
        function(data) {
            return cb(data['app_name'], data['consumer_id']);
        });
};

var consumeLogs = function(consumerId) {
    if (!$('#stream-new-checkbox').is(':checked')) {
        return;
    }
    $.ajax({
        url: 'http://127.0.0.1:60912/consume/' + consumerId,
        success: function(data) {
            logContainer = $('#log-container');
            logContainer.append(data['logs']);
            logContainer.scrollTop(logContainer[0].scrollHeight);
            $('#status').text('Status: ' + data['status']);
        },
        error: function() {
            $('#status').text('Got an error talking to Dusty daemon, streaming is inoperable');
            window.clearInterval(consumeInterval);
        }
    });
};

var checkServiceAvailability = function(consumerId) {
    $.ajax({
        url: location.href,
        success: function(data) {
            location.reload();
        }
    });
};
