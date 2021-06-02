d3.json("/api/data-science/job-openings").then(data => {
    console.log(data);
});

d3.json("/api/data-science/highest-demand").then(data => {
    console.log(data);
});

d3.json("/api/data-science/average-salary").then(data => {
    console.log(data);
});
