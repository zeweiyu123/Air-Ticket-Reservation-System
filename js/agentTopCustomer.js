google.charts.load("current", { packages: ["bar"] });
google.charts.setOnLoadCallback(drawBarChart2);

const person1 = ppl1[0];
const person2 = ppl1[1];
const person3 = ppl1[2];
const person4 = ppl1[3];
const person5 = ppl1[4];
const num1 = tickets[0];
const num2 = tickets[1];
const num3 = tickets[2];
const num4 = tickets[3];
const num5 = tickets[4];

function drawBarChart2() {
  var data = new google.visualization.arrayToDataTable([
    ["Tickets", "#tickets"],
    [person1, num1],
    [person2, num2],
    [person3, num3],
    [person4, num4],
    [person5, num5],
  ]);

  var options = {
    // width: 800,
    legend: { position: "none" },
    chart: {
      title: "Top 5 Customers",
      subtitle: "based on #tickets in the past 6 months",
    },
    axes: {
      x: {
        0: { side: "bottom", label: "#tickets in the past 6 months" },
      },
    },
    bar: { groupWidth: "50%" },
  };

  var chart = new google.charts.Bar(document.getElementById("left"));
  // Convert the Classic options to Material options.
  chart.draw(data, google.charts.Bar.convertOptions(options));
}
