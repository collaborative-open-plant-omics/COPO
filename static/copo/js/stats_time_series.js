async function draw_line_graph() {

    const dataset = await d3.json("/api/stats/combined_stats_json")
    // accessors
    console.log(dataset)


    let dimensions = {
        width: $("#graph").innerWidth() * 0.7,
        height: window.innerHeight * 0.7,
        margin: {
            top: 30,
            right: 15,
            bottom: 100,
            left: 100,
        },
    }
    dimensions.boundedWidth = dimensions.width
        - dimensions.margin.left
        - dimensions.margin.right
    dimensions.boundedHeight = dimensions.height
        - dimensions.margin.top
        - dimensions.margin.bottom


    //Draw canvas
    const wrapper = d3.select("#graph")
        .append("svg")
        .attr("width", dimensions.width)
        .attr("height", dimensions.height)

    const bounds = wrapper.append("g")
        .style("transform", `translate(${
            dimensions.margin.left
        }px, ${
            dimensions.margin.top
        }px)`)

    bounds.append("g")
        .attr("class", "x-axis")
        .style("transform", `translateY(${dimensions.boundedHeight}px)`)
        .append("text")
        .attr("class", "x-axis-label")
        .attr("x", dimensions.boundedWidth / 2)
        .attr("y", dimensions.margin.bottom - 10)

    bounds.append("g").append("path")
        .attr("class", "line")
        .style("transform", "none")
        .style("fill", "none")
        .style("stroke", "steelblue")
        .style("stroke-width", "3")
    bounds.append("g")
        .attr("class", "y-axis")

    bounds.append("g")
        .append("text")
        .attr("class", "y-axis-label")


    function update(metric) {
        console.log(metric)
        const listeningRect = bounds.append("rect")
            .attr("class", "listening-rect")
            .attr("width", dimensions.boundedWidth)
            .attr("height", dimensions.boundedHeight)
            .on("mousemove", onMouseMove)
            .on("mouseleave", onMouseLeave)
        const updateTrans = d3.transition().duration(600).ease(d3.easeSinInOut)
        const yAccessor = d => d[metric]
        const dateParser = d3.timeParse("%Y-%m-%d")
        const xAccessor = d => dateParser(d.date)
        // scales
        const yScale = d3.scaleLinear()
            .domain(d3.extent(dataset, yAccessor))
            .range([dimensions.boundedHeight, 0])
            .nice()
        const xScale = d3.scaleTime()
            .domain(d3.extent(dataset, xAccessor))
            .range([0, dimensions.boundedWidth])
            .nice()
        //draw
        const lineGenerator = d3.line()
            .curve(d3.curveMonotoneX)
            .x(d => xScale(xAccessor(d)))
            .y(d => yScale(yAccessor(d)))

        const line = bounds.select(".line")
            .transition(updateTrans)
            .attr("d", lineGenerator(dataset))


        let dots = bounds.selectAll("circle")
            .data(dataset)

        dots.transition()
            .duration(750)
            .attr("cx", d => xScale(xAccessor(d)))
            .attr("cy", d => yScale(yAccessor(d)))
            .attr("r", 2)

        const old_dots = dots.exit().selectAll("circle").remove()
        dots.enter()
            .append("circle")
            .attr("cx", d => xScale(xAccessor(d)))
            .attr("cy", d => yScale(yAccessor(d)))
            .attr("r", 2)
            .attr("fill", "black")


        // Draw peripherals

        const yAxisGenerator = d3.axisLeft()
            .scale(yScale)
            .ticks(10, ",d")


        const yAxis = bounds.select(".y-axis")
            .transition(updateTrans)
            .call(yAxisGenerator)


        const xAxisGenerator = d3.axisBottom()
            .scale(xScale)
            .tickFormat(d3.timeFormat("%Y-%m-%d"))


        const xAxis = bounds.select(".x-axis")
            .transition(updateTrans)
            .call(xAxisGenerator)
            .style("transform", `translateY(${
                dimensions.boundedHeight
            }px)`)
            .selectAll("text")
            .style("text-anchor", "end")
            .attr("dx", "-.8em")
            .attr("dy", ".15em")
            .attr("transform", "rotate(-65)");

        const yAxisLabel = bounds.select(".y-axis-label")


            .attr("y", 0 - dimensions.margin.left / 2)
            .attr("x", 0 - dimensions.boundedHeight / 2)
            .attr("transform", "rotate(-90)")

            .text("number of " + metric)
            .attr("fill", "black")
            .attr("font-size", "1.4em")
            .style("text-anchor", "middle")

        const tooltip = d3.select("#tooltip")
        const tooltipCircle = bounds.append("circle")
            .attr("r", 6)
            .attr("stroke", "white")
            .attr("fill", "steelblue")
            .attr("stroke-width", 2)
            .style("opacity", 0)

        tooltip.select("#metric")
            .text(metric)

        function onMouseMove(e, datum) {
            const mousePosition = d3.pointer(e)
            const hoverDate = xScale.invert(mousePosition[0])
            const getDistanceFromHoverDate = d => Math.abs(
                xAccessor(d) - hoverDate
            )
            const closestIndex = d3.scan(dataset, (a, b) => (
                getDistanceFromHoverDate(a) - getDistanceFromHoverDate(b)
            ))
            const closestDataPoint = dataset[closestIndex]
            const closestXValue = xAccessor(closestDataPoint)
            const closestYValue = yAccessor(closestDataPoint)
            const formatDate = d3.timeFormat("%B %A %-d, %Y")
            tooltip.select("#date")
                .text(formatDate(closestXValue))

            const formatTemp = d => `${d3.format(".1f")(d)}F`
            tooltip.select("#num_metric")
                .text(closestYValue)

            const x = xScale(closestXValue) + dimensions.margin.left
            const y = yScale(closestYValue) + dimensions.margin.top

            tooltip.style("transform", `translate(`
                + `calc(-50% + ${x}px),`
                + `calc(-100% + ${y}px)`
                + `)`
            )
            tooltipCircle
                .attr("cx", xScale(closestXValue))
                .attr("cy", yScale(closestYValue))
                .style("opacity", 1)
            tooltip.style("opacity", "1")

        }

        function onMouseLeave() {
            tooltip.style("opacity", "0")
            tooltipCircle.style("opacity", "0")
        }

    }


    const metrics = [
        "samples",
        "datafiles",
        "profiles",
        "users",

    ]
    let selectedMetricIndex = 0
    $(document).on("change", "#changeChartMetric", function () {
        var val = $(this).children("option:selected").val()
        var selectedMetricIndex = parseInt(val)
        update(metrics[selectedMetricIndex])
    })
    update(metrics[0])
}

draw_line_graph()


