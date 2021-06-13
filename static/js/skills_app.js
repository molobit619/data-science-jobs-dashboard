d3.json("/api/data-science/skills/totals_by_technology").then(function(response) {
  createBarPlot(response);
}).catch(function(error) {
  console.log(error);
});
