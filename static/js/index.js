var wardCategories = []
var selectedWardPresent = false
$(document).ready(function () {
    // Predict Form
    $("#predict-form").submit(function (event) {
      console.log('form submitted')
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
          console.log(data)
          const twelveMonthPredictions = data.year_predictions.reverse()
          wardCategories = data.wards_categories
          const tables = $('#tables-section table tbody')
          tables.empty()
           
          twelveMonthPredictions.forEach((prediction, index) => {
            Object.entries(prediction).forEach(([zone, value], idx) => {
              if (zone == 'date') return; 
              let _zone;  
              const selectedWard = getSelectedWard(zone)
              if (!selectedWardPresent && selectedWard) {
                _zone = selectedWard.replace(' Ward', '');
                _zone = `<td class="bg-info">${_zone}</td>`;
                selectedWardPresent = true;
              } else {
                _zone = getRandomWard(zone).replace(' Ward', '');
                _zone = `<td>${_zone}</td>`;
              }
              tables.eq(idx).append(`
                <tr>
                  ${zone == 'R1' ? `<td>${formatDate(prediction['date'])}</td>` : ``}
                  ${_zone}
                  <td>${parseFloat(value/4000)}</td>
                </tr>
              `)
            })
          })
          selectedWardPresent = false;
          $("#map").attr('src', '../maps/nairobi_map.html')
        })
        .fail((err) => {
          console.error(err);
        })
        .always(() => {
          console.log("Prediction complete");
        });
    });
});

function getSelectedWard(zone) {
  const selectedWard = wardCategories.find(wc => (wc.category == zone) && wc.ward.includes($('#ward').val()))?.ward;
  wardCategories = wardCategories.filter(wc => wc.ward != selectedWard);
  return selectedWard;
}

function getRandomWard(zone) {
  const filteredWards = wardCategories.filter(wc => wc.category == zone)
  const randomWard =  filteredWards[Math.random() * filteredWards.length | 0].ward
  wardCategories = wardCategories.filter(wc => wc.ward != randomWard)
  return randomWard
}

function formatDate(timestamp) {
  const date = new Date(timestamp);
  const year = date.getFullYear();
  const month = (date.getMonth() + 1).toString().padStart(2, '0'); 
  return `${year}/${month}`
}