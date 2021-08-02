google.charts.load("current", { packages: ["bar"] });
google.charts.setOnLoadCallback(drawBarChart2);

// const time0 = new_time[0];
// const time1 = new_time[1];
// const monthticket0 = new_monthticket[0];
// const monthticket1 = new_monthticket[1];
const time0 = new_time;
const monthticket0 = new_monthticket;

function drawBarChart2() {
  // var data = new google.visualization.arrayToDataTable([
  //   ["Month", "#tickets"]
    // [time0, monthticket0]
    // [time1, monthticket1],
    
  // ]);
//   for (var i = 0; i < time0.length; i++) {
//     data.addRow([time0[i], monthticket0[i]]);
// }
  var d=[];
  var Header= ["Month", "#tickets"];
  d.push(Header);
  for (var i = 0; i < time0.length; i++) {
      var temp=[];
      temp.push(time0[i]);
      temp.push(monthticket0[i]);

      d.push(temp);
  }
  var data = new google.visualization.arrayToDataTable(d);

  var options = {
    width: 800,
    legend: { position: "none" },
    chart: {
      title: "amounts of ticket sold",
      subtitle: "based on #tickets monthly",
    },
    axes: {
      x: {
        0: { side: "bottom", label: "#tickets monthly" },
      },
    },
    bar: { groupWidth: "50%" },
  };

  var chart = new google.charts.Bar(document.getElementById("ticket_graph"));
  // Convert the Classic options to Material options.
  chart.draw(data, google.charts.Bar.convertOptions(options));
}
