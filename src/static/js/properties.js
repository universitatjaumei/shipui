$.fn.serializeObject = function ()
{
  var o = {};
  var a = this.serializeArray();
  $.each(a, function () {
    if (o[this.name] !== undefined) {
      if (!o[this.name].push) {
        o[this.name] = [o[this.name]];
      }

      o[this.name].push(this.value || '');
    } else {
      o[this.name] = this.value || '';
    }
  });

  return o;
};

function loadAppList() {
  $.ajax({
    dataType: 'json',
    url: '/api/apps',
    success: function (data) {
      var $options = $('#apps');
      $options.append($('<option />'));

      for (var key in data) {
        $options.append($('<option />').text(key));
      }
    },
  });
}

$(document).ready(function () {
  loadAppList();

  $('#apps').change(function (e) {
    var app = e.target.value;

    $.ajax({
      url: '/properties/' + app,
      success: function (data) {
        $('textarea[name=props]').val(data);
      },
    });
  });

  $('#update-config').click(function (e) {
    var app = $('#apps').val();

    console.log(app);

    $.ajax({
      url: '/properties/' + app,
      method: 'PUT',
      data: {
        props: $('textarea[name=props]').val(),
      },
      success: function (data) {
        $('textarea[name=props]').val(data);
      },
    });
  });

  $('#new-config').click(function (e) {
    var formData = $('#form-new').serializeObject();

    $.ajax({
      url: '/properties/' + formData.app,
      method: 'POST',
      data: {
        host: formData.host,
      },
      success: function (data) {
        window.location.reload();
      },

      error: function (data) {
        if (data.responseText.indexOf('App already exists') >= 0) {
          alert('La aplicación ya estaba registrada con anterioridad');
        }
      },
    });
  });

  $('#delete-config').click(function (e) {
    var formData = $('#form-new').serializeObject();

    $.ajax({
      url: '/properties/' + formData.app,
      method: 'DELETE',
      success: function (data) {
        window.location.reload();
      },
    });
  });
});
