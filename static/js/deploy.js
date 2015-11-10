function showMessageDeploying() {
  $('.deploying-message').show();
  $('.deploying-message').removeClass('success');
  $('.deploying-message .spinner').show();
  $('.deploying-message .sk-folding-cube').hide();
  $('.deploying-message .title').html('Deploying...');

  $('.log').css('opacity', '1.0');
  $('.log').css('border', '1px solid #AAA');
}

function showMessageDeployFinished() {
  $('.deploying-message').addClass('success');
  $('.deploying-message .spinner').hide();
  $('.deploying-message .sk-folding-cube').show();
  $('.deploying-message .title').html('Done!');
}

$(document).ready(function() {

  $('form button').click(function() {
    //socket.emit('deploy start event', {data: $("select option:selected").text()});
    showMessageDeploying();

    $.ajax({
      type: 'POST',
      url: $('form.deploy-form').attr('action'),
      data: JSON.stringify({ app: $('select option:selected').data('alternative') }, null, '\t'),
      contentType: 'application/json;charset=UTF-8',
      success: function(data, status) {
        showMessageDeployFinished();
      },
    });

    return false;
  });

  return;

  var socket = io.connect('http://' + document.domain + ':' + location.port + '/deploy');
  socket.on('disconnect', function() {
    console.log('disonnected');
  });

  socket.on('deploy-log', function(response) {
    $('pre.log').html(ansispan(response.data));
    socket.emit('received', 'ok');
  });

  socket.on('deploy finished event', function(response) {
    var current = $('pre.log').html();
    $('pre.log').html(current + '\nFinished.\n');
    running = false;
    $('.double-bounce1, .double-bounce2').hide();
  });

});
