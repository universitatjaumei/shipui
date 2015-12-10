var socket = io.connect('http://' + document.domain + ':' + location.port + '/deploy');

function showMessageDeploying() {
  socket.emit('clear-log', {});

  $('.log').show();
  $('.deploying-message').show();
  $('.deploying-message').removeClass('success');
  $('.deploying-message .spinner').show();
  $('.deploying-message .checkok').hide();
  $('.deploying-message .title').html('Deploying...');

  $('.log').html('');
  $('.log').css('opacity', '1.0');
  $('.log').css('border', '1px solid #AAA');

}

function showMessageDeployFinished() {
  $('.deploying-message').addClass('success');
  $('.deploying-message .spinner').hide();
  $('.deploying-message .checkok').show();
  $('.deploying-message .title').html('Done!');
}

function fillProjectBranches(projectID) {
  $.get('/deploy/branches', { projectID: projectID }, function(data, status) {
    var branches = data.branches;
    $('select[name="branch"]').show();

    var branchesSelect = $('select[name="branch"]');
    branchesSelect.empty();
    branchesSelect.append('<option value="trunk">trunk</option>');
    for (var i in branches) {
      branchesSelect.append('<option value="' + branches[i] + '">' + branches[i] + '</option>');
    }

    console.log(data);
  });
}

function getSelectedProject() {
  return $('select[name="app"] option:selected').val();
}

$(document).ready(function() {

  $('form button').click(function() {
    //socket.emit('deploy start event', {data: $("select option:selected").text()});
    showMessageDeploying();

    $.ajax({
      type: 'POST',
      url: $('form.deploy-form').attr('action'),
      data: JSON.stringify({ app: $('select[name=app] option:selected').val(),
                             path: $('select[name=app] option:selected').data('alternative'),
                            }, null, '\t'),
      contentType: 'application/json;charset=UTF-8',
      success: function(data, status) {
        showMessageDeployFinished();
      },
    });

    return false;
  });

  fillProjectBranches(getSelectedProject());

  $('select[name=app]').change(function() {
    console.log('hola');
  });

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
