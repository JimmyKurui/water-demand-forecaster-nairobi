$(document).ready(function () {
    // Predict Form
    $("#predict-form").submit(function (event) {
      event.preventDefault();
  
      var formData = {
        ward: $("#ward").val(),
        month: $("#month").val(),
      };

      $.ajax({
        type: "POST",
        url: predictUrl,
        data: formData,
        dataType: "json",
        encode: true,
      })
        .done((data) => {
          console.log(data);
          $("#map").attr('src', '../maps/nairobi_map.html')
        })
        .fail((err) => {
          console.error(err);
        })
        .always(() => {
          console.log("AJAX request complete");
        });
    });
  });
  