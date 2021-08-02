google.charts.load("current", { packages: ["bar"] });
google.charts.setOnLoadCallback(drawBarChart2);

function drawBarChart2() {
  const arrayLength = monthly_spendings.length;
  let content = [["Commission", "amount of commission"]];
  for (var i = 0; i < arrayLength; i++) {
    content.push([months[i], monthly_spendings[i]]);
  }

  var data = new google.visualization.arrayToDataTable(content);

  var options = {
    // width: 800,
    legend: { position: "none" },
    chart: {
      title: "Monthly Spendings",
    },
    axes: {
      x: {
        0: { side: "bottom", label: "monthly spending" },
      },
    },
    bar: { groupWidth: "50%" },
  };

  var chart = new google.charts.Bar(
    document.getElementById("cusMonthlySpending")
  );
  // Convert the Classic options to Material options.
  chart.draw(data, google.charts.Bar.convertOptions(options));
}
