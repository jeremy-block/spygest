var userCounts = [8, 8, 8]
var json, orignaljson
var entities;
var segments;
var participantData
var participantSegments
var data = []
var tooltip
var card
var cardDivs
var cardField
var cardWidth = 700
var cardHeight = 200
var transitionTime = 750
var segI
var DS = 1
var P = 1
var detailed = true
var prevDocs = []
var showNotes = true
var showTimeline = false;
var moving = false;
var colors = {
  "Doc_open":"crimson",
  "Documents Opened":"crimson",
  "Search":"#009420",
  "Searches":"#009420",
  "Add note":"#4278f5",
  "Notes":"#4278f5",
  "Highlight":"#ab8300",
  "Highlights":"#ab8300",
  "Reading":"pink",
  "barBG": "lightgrey",
  "Average-neg":"blue",
  "Average-pos": "orange",
}
let numberPattern = /\d+/g;



async function startup() {
  docs = [];
  logs = [];
  superlatives = [];
  const fetch_d1 = await fetch(
    "./data/Dataset_1/Documents/Documents_Dataset_1.json"
  );
  const fetch_d2 = await fetch(
    "./data/Dataset_2/Documents/Documents_Dataset_2.json"
  );
  const fetch_d3 = await fetch(
    "./data/Dataset_3/Documents/Documents_Dataset_3.json"
  );
  const fetch_e1 = await fetch(
    "./data/Dataset_1/Documents/Entities_Dataset_1.json"
  );

  Promise.all([fetch_d1, fetch_d2, fetch_d3, fetch_e1])
    .then(async (responses) => {
      for (const response of responses) {
        // console.log(response.json())
        // console.log(`${response.url}: ${response.status}`); //Shows the response for each data file should be the file name and 200
        await response.json().then((data) => {
          docs.push(data);
          // console.log(docs);
        });
      }
      console.log("datasets are loaded:", docs); //Shows that the data is loaded
      Promise.all([await fetch("ApplicationManifest.json")]).then(
        async (mainSegPromise) => {
          // console.log(mainSegPromise);
          for (const res of mainSegPromise) {
            // console.log(`${res.url}: ${res.status}`); //Shows the response for each data file should be the file name and 200
            await res.json().then((json2) => {
              //unwrap json
              orignaljson = Object.assign({}, json2);
              json = json2;
              console.log("segmentation is loaded:", json2);
              logs = json2.interactionLogs;
              console.log(logs[0])
              segments = json2.segments;
              console.log(segments)
              superlatives = json2.superlatives
              for (var seg of segments) {
                seg.annotation = "";
              }
            });
          }
          processData();
          var startTime = 0;
          var endTime = participantSegments[participantSegments.length - 1].end;
          // console.log(endTime);
          console.log(participantSegments);
          drawOverview();
          drawCards(startTime, endTime);

          //add separate tooltip div
          tooltip = d3
            .select("body")
            .append("div")
            .attr("class", "tooltip")
            .style("opacity", 0);
        }
      );
    })
    .catch((error) => {
      console.error(`error encountered in startup: ${error}`);
    });
}

startup()

  function reload(){
    segments.sort(function(a,b){return a.dataset-b.dataset || a.pid-b.pid || a.start-b.start})
    for(var j=0; j<segments.length;j++)
      segments[j].sid=j
    //console.log(segments)

    Promise.all([processData()]).then(function(){
      var startTime = 0;
      var endTime = participantSegments[participantSegments.length-1].end
      //console.log(endTime)
      drawCards(startTime, endTime)
    })
  }

function loadData() {
  json = Object.assign({}, orignaljson)
  logs = json.interactionLogs
  segments = json.segments
  participantData = []
  participantSegments = []
  data = []

  processData();

  var startTime = 0;
  var endTime = participantSegments[participantSegments.length - 1].end
  // console.log(endTime)
    
  if (DS == 3 && P == 4) {
    drawNoData();
  } else if (DS == 2 && P == 3) {
    drawNoData();
  } else if (DS == 2 && P == 7) {
      drawNoData();      
    } else if(DS == 4 && P >= 8 || DS < 4) {
      drawOverview();
      drawCards(startTime, endTime)
    } else {
      drawNoData()
    }
 }

 function saveData(){
    var obj ={}
    obj.segments=segments
    obj.interactions = logs

  	//Convert JSON Array to string.
    var json2 = JSON.stringify(obj);

    //Convert JSON string to BLOB.
    json2 = [json2];
    var blob1 = new Blob(json2, { type: "text/plain;charset=utf-8" });

    //Check the Browser.
    var isIE = false || !!document.documentMode;
    if (isIE) {
      window.navigator.msSaveBlob(blob1, "data.json");
    } else {
      var url = window.URL || window.webkitURL;
      link = url.createObjectURL(blob1);
      var a = document.createElement("a");
      a.download = "data.json";
      a.href = link;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
  }}

  function processData(){
    summary = []
    data=[]
  	var form = document.getElementById("controlForm")
  	DS = document.querySelector('input[name="dataset"]:checked').value;
    P = document.querySelector('input[name="pid"]:checked').value;
  	detailed = document.querySelector('input[name="detailed"]').checked;
    showNotes = document.querySelector('input[name="notes"]').checked;
    showTimeline = document.querySelector('input[name="timeline"]').checked;
    cardWidth = 510;
    cardHeight = 200;
  	participantData = logs[DS-1][P-1]
    // Make the "text" attribute the title for interactions of type "Doc_open" and "Reading" and add the date
    for (var i = 0; i<participantData.length; i++){
      // console.log("participantData")
      // console.log(participantData[i])
      if (DS < 3) {
      if (participantData[i].interactionType == "Doc_open" || participantData[i].interactionType == "Reading"){
        // Get the number from the ID and then subtract 1 to make it the index
        // docPos = parseInt(participantData[i].text.substring(participantData[i].text.indexOf(' ') + 1)) - 1
        docPos = participantData[i].id.match(numberPattern)[0]; //get first number returned in document id
        docPos = docPos - 1 //Have to subtract one, since we're using this to get the index from an array of documents.
        // console.log("docPos", docPos);
        
        //Select the document set from the ID
        if (participantData[i].id.startsWith("armsdealing")) {
          docSet = 0;
        } else if (participantData[i].id.startsWith("terroristactivity")) {
          docSet = 1;
        } else if (participantData[i].id.startsWith("disappearance")) {
          docSet = 2;
        }
        //Function to find the name of a document in the json.
        var searchTest = function (varToSearch, jsonData) {
          for (var key in jsonData) {
            if (typeof jsonData[key] === "object") {
              searchTest(varToSearch, jsonData[key]);
            } else {
              if (jsonData[key] == varToSearch) {
                console.log("found", jsonData[key]);
              }
            }
          }
        };

        // Split the title into the date and actual title
        // console.log("docs")
        // console.log(docs[docSet][i]);
        // console.log("docSet", docSet);
        // thisDoc = searchTest(docPos, docs)
        // print(thisDoc)
        docDate = docs[docSet][docPos].date; 
        docTitle = docs[docSet][docPos].title;
      } else {
        docSet = 3;
        if (participantData[i].interactionType == "Reading") {
          docPos = 3 //TODO Make this work better 
        }
          docDate = "November 2022";
        }
        // Modify the participantData array
        // participantData[i].text = docTitle
        //TODO: Line of code above works but breaks identifying the docset upon going back, can't find the reference to this value to change it need to ask Brett
        participantData[i].date = docDate
      }
    }
  	participantSegments = GetSegments(DS,P)
  	participantData = segmentify(participantSegments, participantData)


  	//Summarize segments, get some more stats
  	var total_interactions = 0;
    prevDocs = []
  	for (var i = 0; i<participantData.length; i++){
      segI = i
  		var summary = summarize_segment(participantData[i])
  		summary.pid = P;
  		summary.dataset = DS
  		summary.number = i
      summary.keywords = participantSegments[i].keywords
  		if(summary.interesting)
  			total_interactions += summary.total_interactions;
  		data.push(summary)
  	}
    // console.log(data)

  	var totalSummary = GetAllCounts(data);
  	//Stats
    var exp_avg_interaction_rate = total_interactions / participantData.length //get the average number of interactions expected per segment
    var maxDiff = 0;
  	for(var seg of data){
      seg.interaction_rate = Math.max(0, (seg.total_interactions / total_interactions));
      seg.interaction_diff_from_average = seg.total_interactions - exp_avg_interaction_rate;
      maxDiff = Math.max(maxDiff, Math.abs(seg.interaction_diff_from_average)) //Determine the maximum expected interaction rate difference for all segments.
    }
    // Assign a ratio value for bar chart
    for (var seg of data) {
      seg.interaction_ratio_from_average = seg.interaction_diff_from_average / maxDiff
    }

  }

function drawNoData() {
  console.log("Current Combination is not available")
  d3.selectAll("#overview p").remove();
  d3.select("#overview")
    .append("p")
    .attr("class", "errorNote")
    .attr("style", "background-color:wheat")
    .html("No summary");
  d3.selectAll("#chartArea").remove();
  d3.select("#chart")
    .style("display", "block")
    .append("div")
    .attr("id", "chartArea")
    .append("h3")
    .attr("class", "errorNote")
    .html("<strong>No data for the currently selected combination </strong>")
}
  /**
   * This is the overview paragraph that would describe what's going on at a high level - no segments. 
   * It would report on things like:
   *    Longest Segment
   *    Shortest Segment
   *    How did they find topics (mostly search lead or serendipity lead?)
   *    Hub and spoke or more linear?
   *    Number of topics explored
   *    Most explored topic - Most repeatedly explored topics
   *    Least explored topic
   *    Number of searches
   *    Number of unique documents opened / vs number of documents opened in total / vs number of documents in the dataset (percent of dataset explored)
   *    Most common interaction type
   *    Most common interaction sequences
   */
function drawOverview() {
  function applyHTMLHighlight(text) {
    return "<span class='highlightHTML'>" + text + "</span>"
  }
  function applyHTMLHighlightSegment(value) {
    return "<span class='highlightSegment'>#" + value + "</span>"
  }
  function topicsToHighlightText(listOfTopics, numberOfTopics = 3) {
    output = "";
    for (word = 0; word < numberOfTopics - 1; word++) {
      output += applyHTMLHighlight( listOfTopics[word]) +", "
    }
    output +=
      "and " + applyHTMLHighlight(listOfTopics[numberOfTopics - 1]);
    return output
  }
  
  supers = superlatives[DS-1][P-1]
  // console.log(supers)

  d3.select("#overview")
    .selectAll("p")
    .remove()
  overview = d3
    .select("#overview")
    .append("p")
    .html(
      "They focused on <strong>" +
        supers["topicCount"] +
        "</strong> identified topics in this analysis session, exploring <strong>" +
        Math.round(100 * supers["dataCoverage"]) +
        "%</strong> of the dataset. The topics that received the most attention were <strong>" +
        topicsToHighlightText(supers["topics"]) +
        "</strong>. They started searching for <strong>" +
        applyHTMLHighlight(supers["breakpointSearches"][0]) +
        "</strong>, before transitioning to <strong>" +
        applyHTMLHighlight(supers["breakpointSearches"][1]) +
        "</strong> and finally looking for <strong>" +
        applyHTMLHighlight(supers["breakpointSearches"][2]) +
        "</strong>. The segment with the newest content was <strong>" +
        applyHTMLHighlightSegment(supers["newestSeg"]) +
        "</strong>. Segment <strong>" +
        applyHTMLHighlightSegment(supers["longSeg"]) +
        "</strong> was the longest period where they were <strong>" +
        supers["longOpenRate"] +
        "</strong>. They conducted <strong>" +
        supers["searchCount"] +
        "</strong> searches throughout their session, especially in segment <strong>" +
        applyHTMLHighlightSegment(supers["mostSearchSeg"]) +
        "</strong>."
    );
}

function drawCards(startTime, endTime){
	//draw cards
	d3.selectAll("#chartArea").remove()
	d3.select("#chart").style("display", "block").append("div").attr("id","chartArea")


  cardDivs = d3.select("#chartArea").selectAll("field").data(data).enter().append("div").
    attr("id", function (d, i) {
      return "cardDiv"+ d.pid + "_" +d.number
    })
    // .style("margin-bottom", "15px")
    // .style("margin-left", "15px")
    // .style("margin-right", "15px")
    .style("display", "inline-block")


	card = cardDivs.append("svg").
    attr("height", cardHeight).
    attr("width", cardWidth).
    style("display", "block").
    attr("id",function(d){
     return "card" + d.pid + "_" +d.number
    }).
    style("fill-opacity", "0.7").
    style("stroke-opacity", "0.7")
    .on("mouseover", function (d, i) {
      // console.log(i);
      var selectID = "#card" + i.pid+"_"+i.number
      d3.select(selectID)
        .style("fill-opacity", "1.0")
        .style("stroke-opacity", "1.0")
    })
    .on("mouseout", function (d, i) {
      // console.log(d,i);
      var selectID = "#card" + i.pid+"_"+i.number
      d3.select(selectID)
        .style("fill-opacity", "0.7")
        .style("stroke-opacity", "0.7")
    })

  if(showNotes){
    cardField = cardDivs.append("div")
    cardField.append("p").html("<b>Notes:</b>").attr("class","tooltipP")
    cardField.append("textarea")
      .property("value", function(d,i){
        var seg = GetSegment(d.number, d.pid, d.dataset)
        return seg.annotation
      })
      .style("width", cardWidth)
      .style("height", "100")
      .attr("id", function(d,i){return "cardField" + d.pid + "_" +d.number})
      .on("input",function(d,i){
        //save notes to seg json as they are written
        var val = cardDivs.select("#cardField" + d.pid + "_" +d.number).property("value")
        var seg = GetSegment(d.number, d.pid, d.dataset)
        seg.annotation = val
      })
  }


	//background rect
	card.bg = card.append("rect").
    attr("x",5).
    attr("y",5).
    //attr("rx", 5).
    attr("height", cardHeight-10).
    attr("width",cardWidth-10).
    style("fill","white").
    style("stroke", "navy").
    style("stroke-width", 3)

	//segment label
	card.label = card
    .append("text")
    .attr("x", 15)
    .attr("y", 25)
    .text(function (d) {
      var segment = GetSegment(d.number, d.pid, d.dataset);
      // console.log(segment)
      return (
        "#" +
        (d.number + 1) +
        " | " +
        IntToTime(segment.end - segment.start) +
        " minutes"
      );
    })
    .on("mouseover", function (d, i) {
      var seg = GetSegment(d.number, d.pid, d.dataset);
      tooltip.transition().duration(100).style("opacity", 1.0);

      tooltip
        .html(TimeToolTip(seg))
        .style("left", d3.event.pageX + "px")
        .style("top", d3.event.pageY - 28 + "px");
    })
    .on("mouseout", function (d, i) {
      tooltip.transition().duration(100).style("opacity", 0.0);
    })
    .on("mousemove", function (d, i) {
      tooltip
        .style("left", d3.event.pageX + "px")
        .style("top", d3.event.pageY - 28 + "px");
    });

  card.divider = card.append("line")
        .attr("x1",10)
        .attr("y1",33)
        .attr("x2",cardWidth-10)
        .attr("y2",33)
        .attr("stroke-width",1)
        .attr("stroke","grey")

  card.text = cardText(card)

  card.timeline = timelineElement(card, startTime, endTime);

  if(detailed){

    if (showTimeline) {
      card.segmentTimeline = segmentTimelineElement(card);
    }
    
    var barY = cardHeight-20
    
    //interaction bars
    card.search = barElement(card, 15, barY, "Searches", "🔎", function(d){ return 25*(d.local_search_ratio) })
    
    card.highlight = barElement(card, 50, barY, "Highlights", "🔖", function(d){ return 25*(d.local_highlight_ratio) })
    
    card.notes = barElement(card, 85, barY, "Notes", "📝", function(d){ return 25*(d.local_note_ratio) })
    
    card.open = barElement(card, 120, barY, "Documents Opened", "🦄", function(d){ return 25*(d.local_open_ratio) })
    
    card.total = centerBarElement(card,155,barY,"Average","📖",function (d) {return 12.5 * d.interaction_ratio_from_average;});
    
    
  }
}

//Adds the card bullets and paragraph of text from the pre-summarized segment
function cardText(card){
  var element = {}
  var bulletStartY = 150 ;// (0.55*cardHeight)
  if (!detailed) {
    element.descriptionText = card
      .append("text")
      .attr("x", 15)
      .attr("y", function (d, i) {
        return 50;
      })
      .attr("id", "descriptionText")
      .html(function (d, i) {
        if (d.descriptions.length == 0) return;

        var text = "";
        for (var text2 of d.descriptions) text += text2 + "<br> ";

        //d.displayedInfo++
        return text;
      })
      .call(wrap, cardWidth - 25);
  } else {
    //open info
    element.searchText = card
      .append("text")
      .attr("x", 15)
      .attr("y", function (d, i) {
        return bulletStartY - 20 * d.displayedInfo;
      })
      .attr("id", "openText")
      .html(function (d, i) {
        var keys = Object.keys(d.opens);
        // console.log(d.opens)
        if (keys == 0)
          if (d.displayedInfo == 0) {
            d.displayedInfo++;
            return "• No documents were explored.";
          } else return;

        var text =
          "• Explored " +
          keys.length +
          (keys.length == 1 ? " document" : " different documents") +
          ".";
        d.displayedInfo++;
        return text;
      });

    //Note info
    element.noteText = card
      .append("text")
      .attr("x", 15)
      .attr("y", function (d, i) {
        return bulletStartY - 20 * d.displayedInfo;
      })
      .attr("id", "noteText")
      .html(function (d, i) {
        var keys = Object.keys(d.notes);
        if (keys.length == 0) return;

        var text = "• Noted ";
        var slicedText = keys[0].slice(0, 35);
        text +=
          '<tspan style="font-weight:bold;fill:' +
          colors["Notes"] +
          '">' +
          '"' +
          slicedText +
          (keys[0].length == slicedText.length ? "" : "...") +
          '"' +
          "</tspan>.";

        d.displayedInfo++;

        return text;
      })
      .on("mouseover", function (d, i) {
        tooltip.transition().duration(100).style("opacity", 1.0);

        tooltip
          .html(SummaryToolTip(Object.keys(d.notes)[0], "Full Note"))
          .style("left", d3.event.pageX + "px")
          .style("top", d3.event.pageY - 28 + "px");
      })
      .on("mouseout", function (d, i) {
        tooltip.transition().duration(100).style("opacity", 0.0);
      });

    //Keyword info
    element.keywordText = card
      .append("text")
      .attr("x", 15)
      .attr("y", function (d, i) {
        return bulletStartY - 20 * d.displayedInfo;
      })
      .attr("id", "noteText")
      .html(function (d, i) {
        var keys = d.keywords;
        if (keys.length == 0) return;

        var text = "• Keywords: ";
        var slicedText = keys[0];
        for (var i = 1; i < keys.length; i++) {
          // Add something about cutting off at the edge of the card or something, maybe stick with 35? idk
          // Add back hover text --- need to look at the SummaryToolTip function (or just not use it)
          // Function mergecard, maybe modify it to merge the keywords?
          //      current function deletes old segments and melds them into a new one and just yeets the keywords
          slicedText += ", " + keys[i];
        }
        text +=
          '<tspan style="font-weight:bold;fill:' +
          colors["Notes"] +
          '">' +
          '"' +
          slicedText +
          (keys[0].length == slicedText.length ? "" : "...") +
          '"' +
          "</tspan>.";

        d.displayedInfo++;

        return text;
      });

    //Highlight info
    element.highlightText = card
      .append("text")
      .attr("x", 15)
      .attr("y", function (d, i) {
        return bulletStartY - 20 * d.displayedInfo;
      })
      .attr("id", "highlightText")
      .html(function (d, i) {
        var keys = Object.keys(d.highlights);
        if (keys.length == 0) return;

        var slicedText = keys[0].slice(0, 35);
        var text =
          "• Highlighted " +
          '<tspan style="font-weight:bold;fill:' +
          colors["Highlight"] +
          '">' +
          '"' +
          slicedText +
          (keys[0].length == slicedText.length ? "" : "...") +
          '"' +
          "</tspan>.";

        d.displayedInfo++;

        return text;
      })
      .on("mouseover", function (d, i) {
        tooltip.transition().duration(100).style("opacity", 1.0);

        tooltip
          .html(SummaryToolTip(Object.keys(d.highlights)[0], "Full Highlight"))
          .style("left", d3.event.pageX + "px")
          .style("top", d3.event.pageY - 28 + "px");
      })
      .on("mouseout", function (d, i) {
        tooltip.transition().duration(100).style("opacity", 0.0);
      });

    element.searchText = card
      .append("text")
      .attr("x", 15)
      .attr("y", function (d, i) {
        return bulletStartY - 20 * d.displayedInfo;
      })
      .attr("id", "searchText")
      .html(function (d, i) {
        var keys = Object.keys(d.searches);
        if (keys.length == 0) return;
        var text = "• Searched for ";
        for (var i = 0; i < Math.min(3, keys.length); i++) {
          if (i == Math.min(3, keys.length) - 1 && keys.length != 1)
            text += "and ";

          text +=
            '<tspan style="font-weight:bold;fill:' +
            colors["Search"] +
            '">' +
            keys[i] +
            "</tspan>";

          if (i != Math.min(3, keys.length) - 1) text += ", ";
        }
        d.displayedInfo++;
        text += ".";
        return text;
      });

    return element;
  }
}


//Arguments: The svg element to draw the bar on, x location, y location, text label, function to determine size of bar
//Output: void return, item added to input svg
//example: the mini bars at the bottom for each interaction type
function barElement(card, x, y, text, symbol, sizefunc){
	element = {}
	unselectBar = "royalblue"
	unselectBG = "lightblue"

	element.bar = card.append("line").
    attr("x1",x).
    attr("y1",y+5).
    attr("x2",x+25).
    attr("y2",y+5).
    attr("stroke-width",5).
    attr("stroke-opacity","0.5").
    attr("class", "barBar"+text.replace(/\s+/g, '')).
    style("stroke", colors[text])

  element.bg = card.append("line").
      attr("x1",x).
      attr("y1",y+5).
      attr("x2",function(d,i){return x+sizefunc(d)}).
      attr("y2",y+5).
      attr("stroke-width",5).
      attr("class", "barBG"+text.replace(/\s+/g, '')).
      style("stroke", colors[text])

  element.text = card.append("text").
    attr("x",x).
    attr("y",y-5).
    style("user-select","none").
    html(symbol).
    style("font-size", function(){return (text=="Average"?12:18)}).
    call(wrap, 385)

	//invisible box over bar and lable, to handle interactions for both rects of the bar
	element.selectionArea = card.append("rect").
    attr("x",x).
    attr("y",y-25).
    attr("height", 25+10).
    attr("width",25).
    attr("class", "selectionArea"+text.replace(/\s+/g, '')).
    style("opacity", 0).
    on("mouseover",function(d,i){
      var selectID = "#card" + d.pid+"_"+i

      d3.select(selectID).select(".barBar"+text.replace(/\s+/g, '')).
        style("fill", colors[text]).
        style("fill-opacity", "0.7")

      d3.select(selectID).selectAll(".barBG"+text.replace(/\s+/g, '')).
        style("fill", colors["barBG"]).
        style("fill-opacity", "0.7")

      tooltip.transition().
        duration(100).
        style("opacity", 1.0);

      tooltip.html(BarToolTipText(d,text)).
        style("left", (d3.event.pageX) + "px").
        style("top", (d3.event.pageY - 28) + "px");
    }).
    on("mouseout",function(d,i){
      var selectID = "#card" + d.pid+"_"+i

      d3.select(selectID).selectAll(".barBar"+text.replace(/\s+/g, '')).
        style("fill", colors[text]).
        style("fill-opacity", null)

      d3.select(selectID).selectAll(".barBG"+text.replace(/\s+/g, '')).
        style("fill", colors["barBG"]).
        style("fill-opacity", null)


      tooltip.transition().
        duration(100).
        style("opacity", 0);
    }).
    on("mousemove",function(){
      tooltip.style("left", (d3.event.pageX) + "px")
        .style("top", (d3.event.pageY - 28) + "px");
  })

  return element

}
function centerBarElement(card, x, y, text, symbol, sizefunc) {
  element = {}
  unselectBar = "royalblue"
  unselectBG = "lightblue"

  element.bg = card
    .append("line")
    .attr("x1", x)
    .attr("y1", y + 5)
    .attr("x2", x + 25)
    .attr("y2", y + 5)
    .attr("stroke-width", 8)
    .attr("stroke-opacity", "0.5")
    .attr("class", "barBG" + text.replace(/\s+/g, ""))
    .style("stroke", "#dddddd");

  element.bar = card
    .append("line")
    .attr("x1", function (d, i) {
      return sizefunc(d) > 0 ? x + 12.5 : x + sizefunc(d) + 12.5;
    })
    .attr("y1", y + 5)
    .attr("x2", function (d, i) {
      return sizefunc(d) > 0 ? x + 12.5 + sizefunc(d) : x + 12.5;
    })
    .attr("y2", y + 5)
    .attr("stroke-width", 5)
    .attr("class", "barBar" + text.replace(/\s+/g, ""))
    .style("stroke", function (d, i) {
      return sizefunc(d) > 0 ? colors[text + "-pos"] : colors[text + "-neg"];
    });

  element.center = card
    .append("line")
    .attr("x1", x + 12.5)
    .attr("y1", y + 0)
    .attr("x2", x + 12.5)
    .attr("y2", y + 10)
    .attr("stroke-width", 2)
    .attr("stroke-opacity", "0.9")
    .attr("class", "center" + text.replace(/\s+/g, ''))
    .style("stroke", "#000000");

  element.text = card.append("text").
    attr("x",x).
    attr("y",y-5).
    style("user-select","none").
    html(symbol).
    style("font-size", function(){return (text=="Total"?12:18)}). //Set the font size of the icon - 18 is for icons 12 is for text
    call(wrap, 385)

	//invisible box over bar and lable, to handle interactions for both rects of the bar
	element.selectionArea = card.append("rect").
    attr("x",x).
    attr("y",y-25).
    attr("height", 25+10).
    attr("width",25).
    attr("class", "selectionArea"+text.replace(/\s+/g, '')).
    style("opacity", 0).
    on("mouseover",function(d,i){
      var selectID = "#card" + d.pid+"_"+i

      d3.select(selectID).select(".barBar"+text.replace(/\s+/g, '')).
        style("fill", colors[text]).
        style("fill-opacity", "0.7")

      d3.select(selectID).selectAll(".barBG"+text.replace(/\s+/g, '')).
        style("fill", colors["barBG"]).
        style("fill-opacity", "0.7")

      tooltip.transition().
        duration(100).
        style("opacity", 1.0);

      tooltip.html(BarToolTipText(d,text)).
        style("left", (d3.event.pageX) + "px").
        style("top", (d3.event.pageY - 28) + "px");
    }).
    on("mouseout",function(d,i){
      var selectID = "#card" + d.pid+"_"+i

      d3.select(selectID).selectAll(".barBar"+text.replace(/\s+/g, '')).
        style("fill", colors[text]).
        style("fill-opacity", null)

      d3.select(selectID).selectAll(".barBG"+text.replace(/\s+/g, '')).
        style("fill", colors["barBG"]).
        style("fill-opacity", null)


      tooltip.transition().
        duration(100).
        style("opacity", 0);
    }).
    on("mousemove",function(){
      tooltip.style("left", (d3.event.pageX) + "px")
        .style("top", (d3.event.pageY - 28) + "px");
  })

  return element

}

//creates merge and create new segment buttons
function textButton(card, x, y, text, color, func){
	var element = {}
  element.button = card.append("rect")
    .attr("x",x)
    .attr("y",y)
    .attr("width",function(){return (text=="Create from Selection")?120:25})
    .attr("height",25)
    .attr("fill",color)

  element.text = card.append("text").
    attr("x",x+2).
    attr("y",y+18).
    style("user-select","none").
    text(text).
    style("font-size", function(){return (text=="Create from Selection")?12:16}).
    call(wrap, 385)

  element.buttonHB = card.append("rect")
    .attr("x",x)
    .attr("y",y)
    .attr("width",function(){return (text=="Create from Selection")?120:25})
    .attr("height",25)
    .attr("opacity",0)
    .on("mousedown", func)
    .on("mouseout",function(d,i){

      tooltip.transition().
        duration(100).
        style("opacity", 0);
    }).
    on("mousemove",function(){
      tooltip.style("left", (d3.event.pageX) + "px")
        .style("top", (d3.event.pageY - 28) + "px");
  })

    return element
}

//draws the timeline element on the card
function timelineElement(card, startTime, endTime){
  //timeline stuff
  var element = {}
  var start = 225
  element.sWidth = 10;
  element.clickX1 = -1;
  element.clickX2 = -1;
  var scale = d3.scaleLinear().domain([startTime,endTime]).range([0,cardWidth-10-start])
  var scale2 = d3.scaleLinear().domain([start,cardWidth-10]).range([startTime,endTime])
  element.timeLineBG = card.append("path").
    attr("d",function(d,i){
      //var start = 125
      return d3.line()([[start, 20],[cardWidth-10,20]])
    }).
    attr("stroke","lightblue").
    attr("stroke-width", 15).
    attr('pointer-events', 'visibleStroke')

  element.timeLineBox = card.append("path").
    attr("d",function(d,i){
      var seg = GetSegment(d.number, d.pid, d.dataset)
      //console.log(startTime)
      return d3.line()([[start+scale(seg.start), 20],[start+scale(seg.end),20]])
    }).
    attr("stroke","royalblue").
    attr("stroke-width", 20).
    attr('pointer-events', 'visibleStroke')

  element.timeLineHitbox = card.append("path").
    attr("d",function(d,i){
      return d3.line()([[start, 20],[cardWidth-10,20]])
    }).
    attr("stroke","darkSeaGreen").
    attr("stroke-width", 20).
    attr("stroke-opacity",0).
    attr('pointer-events', 'visibleStroke').
    on("mouseover",function(d,i){
      var seg = GetSegment(d.number, d.pid, d.dataset)
      tooltip.transition().
        duration(100).
        style("opacity", 1.0);

      tooltip.html(TimeToolTip(seg)).
        style("left", (d3.event.pageX) + "px").
        style("top", (d3.event.pageY - 28) + "px");
    }).
    on("mouseout",function(d,i){
      tooltip.transition().
        duration(100).
        style("opacity", 0.0);
    }).
    on("mousemove", function (d, i) {
      // console.log(d, i);
      tooltip.style("left", (d3.event.pageX) + "px").
        style("top", (d3.event.pageY - 28) + "px");

    })

  return element;
}

//adds a segment timeline to each card with all interactions presented.
function segmentTimelineElement(card){
  var element = {}
  element.sWidth = 10;
  element.clickX1 = -1;
  element.clickX2 = -1;

  element.segmentSelectionBG = card.append("path").
    attr("d", d3.line()([[40,45],[cardWidth-40,45]])).
    attr("stroke","lightgrey").
    attr("stroke-width", 10)
  //   .on("mousemove",function(d,i){
  //     tooltip.style("left", (d3.event.pageX) + "px").
  //     style("top", (d3.event.pageY - 28) + "px");

  //     var select = d3.select(".selection" + d.pid + "_" +d.number)
  //     //snap to mouse when selection and area
  //     select.attr("x2", function(d,i){
  //       if(element.clickX1 != -1 && element.clickX2==-1){
  //         return (event.offsetX)
  //       }else
  //         return select.attr("x2")
  //       })
  //   }).
  //   on("mousedown",function(d,i){
  //     var seg = GetSegment(d.number, d.pid, d.dataset)
  //     var scale = d3.scaleLinear().domain([40,cardWidth-40]).range([seg.start,seg.end])
  //     var select = d3.select(".selection" + d.pid + "_" +d.number)
  //     //log first click loc
  //     if(element.clickX1 == -1){
  //       element.clickX1 = event.offsetX
  //       select
  //       .attr("x1", element.clickX1)
  //       .attr("x2", element.clickX1)
  //       .attr("y1",45)
  //       .attr("y2",45)
  //       .style("stroke-opacity", "0.5")
  //       .style("stroke-width", 15)
  //       .style("stroke", "black")
  //     }
  //     //handle second click
  //     else if(element.clickX2 == -1){
  //       element.clickX2 = event.offsetX
  //       select.attr("x2",element.clickX2)

  //       //swap if x1 < x2
  //       if(Number(select.attr("x1"))>Number(select.attr("x2"))){
  //         var temp = select.attr("x2")
  //         select.attr("x2",select.attr("x1"))
  //         select.attr("x1",temp)
  //       }

  //       //reset
  //       element.clickX1=-1
  //       element.clickX2=-1
  //     }
  //   })

  element.segmentTimelineBG = card.append("path").
    attr("d", d3.line()([[40,45],[cardWidth-40,45]])).
    attr("stroke","black").
    attr("stroke-width", 3)

  element.segmentTimelineBG = card.append("g").
    html(function(d,i){
      var html = ""
      var seg = GetSegment(d.number, d.pid, d.dataset)
      var scale = d3.scaleLinear().domain([seg.start,seg.end]).range([40,cardWidth-40])

      //first draw reading
      for(var j=0; j<d.all_interactions.length;j++){
        var int = d.all_interactions[j]
        //only do for reading
        if(int.interactionType!="Reading")
          continue

        var color, x1,x2,y1,y2,stroke
        color = colors["Reading"]
        x1 = scale(int.time/10)
        x2 = Math.min(cardWidth-40,scale((int.time+int.duration)/10)-1)
        y1 = 45
        y2 = 45
        stroke = 15

        var arg = "\""+d.number+"\",\""+j+"\""

        html += "<line x1="+x1+" y1="+y1+" x2="+x2+" y2="+y2+ " style=\"opacity:0.9; stroke:"+color+";stroke-width:"+stroke+"\" onmouseover=segTimelineOver("+arg+") onmouseout=\"segTimelineOut()\" onmousemove=\"segTimelineMove()\" pointer-events:visibleStroke></line>"
      }

      //then draw interactions
      for(var j=0; j<d.all_interactions.length;j++){
        var int = d.all_interactions[j]
        if(int.interactionType=="Reading")
          continue
        var color, x1,x2,y1,y2,stroke

        //colors
        color = colors[int.interactionType]
        //positioning
        switch(int.interactionType){
          default:
            x1 = scale(int.time/10)
            x2 = scale(int.time/10)
            y1 = 45-7.5
            y2 = 45+7.5
            stroke = int.interactionType=="Doc_open"?2:4
        }

        var arg = "\""+d.number+"\",\""+j+"\""

        html += "<line x1="+x1+" y1="+y1+" x2="+x2+" y2="+y2+ " style=\"stroke:"+color+";stroke-width:"+stroke+"\" onmouseover=segTimelineOver("+arg+") onmouseout=\"segTimelineOut()\" onmousemove=\"segTimelineMove()\" pointer-events:visibleStroke></line>"
      }
      return html
    })

  return element
  }

function conditionalQuality(segment){
  var documentInteractionsPerSegment = Math.abs(segment.interaction_ratio_from_average)
  var isPositive = segment.interaction_ratio_from_average > 0 ? true : false
  var quality = ""
  if (documentInteractionsPerSegment > 0.75) {
    if (isPositive) {
      quality =
        "<span>opened <strong>many more</strong> documents than usual</span>";
    } else {
      quality =
        "<span>opened <strong>many fewer</strong> documents than usual</span>";
    }
  } else if (documentInteractionsPerSegment > 0.1) {
    if (isPositive) {
      quality =
        "<span>opened <strong>more</strong> documents than usual</span>";
    } else {
      quality =
        "<span>opened <strong>fewer</strong> documents than usual</span>";
    }
  } else{
    quality =
      "<span>opened the <strong>usual</strong> number of documents in this segment</span>";
  }
  return quality
}


//get html for action bar tooltips
function BarToolTipText(d, type){
  var title = "<b>"+type+" (" + TextToValue(d,type) + ")"
  var text = ""
  var data
  switch(type){
    case "Searches":
    data = d.searches
    break
    case "Highlights":
    data = d.highlights
    break
    case "Notes":
    data = d.notes
    break
    case "Documents Opened":
    data = d.opens
    break
    case "Average":
      var quality = conditionalQuality(d);
    return quality+"<b> Total: (" + TextToValue(d,type) + ")"
  }
  title+= ":</b> <br>"
  var keys = Object.keys(data)
  for(var i=0; i<keys.length;i++){
    text += "#"+(i+1)+": " + keys[i] + ((data[keys[i]]==1?"":" (x" + data[keys[i]]+")"))+"<br>"
  }

  if(text=="")
    text="None"

  return title + "<br>" + text;
}

//gets html for textual summary tooltip
function SummaryToolTip(text, type){
  var title = "<b>"+type+"</b> <br>"
  var text = text

  return title + "<br>" + text;
}

//get html for timeline tooltip
function TimeToolTip(segment) {
  console.log("segment", segment);
	console.log(segment)
  var text ="<p class=\"tooltipP\"><b>"+IntToTime(segment.start) + "-" + IntToTime(segment.end)+"</b> ("+IntToTime(segment.length)+")</p>"
  return text
}

function segTimelineOver(sid, number){
  var int = GetInteraction(sid,number)
  var type = (int.interactionType=="Doc_open")?"Document Opened":int.interactionType
  var time = IntToTime(int.time/10)

  var text
  switch(int.interactionType){
    case "Doc_open":
    text = "Opened <b>" + int.text +"</b>"
    break
    case "Search":
    text = "Searched for <b>" +int.text +"</b>"
    break;
    case "Add note":
    text = "Noted <b>\"" +int.text+"\"</b>"
    break
    case "Highlight":
    text = "Highlighted <b>\"" +int.text+"\"</b> on <b>" +int.id+"</b>"
    break
    case "Reading":
    text = "Reading <b>\"" +int.text+"\"</b> for "+Math.floor(int.duration/10)+" seconds"
    break
  }


  var text2 = "<p class=\"tooltipP\"><b>"+time+"</b><br>"+text+"</p>"
  if(int.interactionType=="Reading")
    text2 = "<p class=\"tooltipP\"><b>"+time+"-"+IntToTime((int.time+int.duration)/10)+"</b> ("+IntToTime(int.duration/10)+")<br>"+text+"</p>"

  tooltip.transition().
    duration(100).
    style("opacity", 1.0);

  tooltip.html(text2).
    style("left", (event.pageX) + "px").
    style("top", (event.pageY - 28) + "px");
}

function segTimelineOut(){
  tooltip.transition().
    duration(100).
    style("opacity", 0);
}

function segTimelineMove(){
  tooltip.style("left", (event.pageX) + "px").
    style("top", (event.pageY - 28) + "px");
}


//Argument: a participant interaction json object
//Result: 	an array of interaction json objects regrouped by segment
function segmentify(segments, interactions){
	var segmented_data = []
	var current_segment = []
	var segment_id = 0

  for(var seg of segments){
    segmented_data.push([])
    seg.sid = segment_id
    segment_id++
  }
  for(var item of interactions){
  	for(var seg of segments){
      if(item.time < seg.end*10 && item.time>seg.start*10){
        //console.log(seg.sid)
        segmented_data[seg.sid].push(item)
      }else if(item.type=="Reading"){
        //include reading if the end is also in the segment
        var endTime = item.time+item.duration
        if(endTime < seg.end*10 && endTime>seg.start*10){
          //console.log(seg.sid)
          segmented_data[seg.sid].push(item)
        }
      }
    }
  }
  // console.log("segmented_data")
  // console.log(segmented_data)
	//push whatever was in the last segment
	//segmented_data.push(current_segment)
	return segmented_data
}


//Argument: a segment from the array returned by segmentify
//Returns:  a json object
function summarize_segment(segment){

///////This is where I sub out "text" to the meaningful titles, maybe also adding the dates as a new attribute

	var opens = []; //opening
  // var openTitles = []; //Meaningful text titles
  // var openDates = []; //The dates associated with the documents if available
	var searches = []; //Search
	var notes = [] //Add note
	var highlights = [] //Highlight
  var readings = [] //reading
  var dates = [] //Dates
  var all_interactions = []
  var total_interactions = 0;
  var openIDs = []

	//collect interesting data from logs, removes non-alphanumeric chars to avoid issues
  // console.log("segment")
  // console.log(segment)
	for(var interaction of segment){
		switch(interaction['interactionType']){
      case "Doc_open":
        console.log(interaction)
      opens.push(interaction["title"]);
      openIDs.push(interaction["id"])
      dates.push(interaction["date"])
      all_interactions.push(interaction)
      total_interactions++
      break
      case "Search":
      searches.push(interaction["text"])
      all_interactions.push(interaction)
      total_interactions++
      break;
      case "Add note":
      notes.push(interaction["text"])
      all_interactions.push(interaction)
      total_interactions++
      break
      case "Highlight":
      total_interactions++
      highlights.push(interaction["text"])
      all_interactions.push(interaction)
      break
      case "Reading":
      dates.push(interaction["date"])
      readings.push(interaction)
      break
    }
  }

  // Sort dates
  var allMonths = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  if (DS < 2) {
    // console.log("dates", dates);
    for (i in dates) {
      // Replace "<month> <year>" with a date object
      dates[i] = new Date(parseInt(dates[i].split(" ")[1]), allMonths.indexOf(dates[i].split(" ")[0]))
    }
    dates.sort(function(a, b){
        return a - b
      });
  }

  var readings_merged = []
  //merge small reading segments
  for(var i = 0; i<readings.length; i++){
    var int = readings[i]
    for(var j=i+1;j<readings.length;j++){

      if(readings[j].text==int.text){
        int.duration = (readings[j].time - int.time) + readings[j].duration
        i=j
      }
      if(readings[j].text!=int.text){
        if(int.duration>100){
          readings_merged.push(int)
          all_interactions.push(int)
        }
        break
      }

    }
    if(i==readings.length-1){
    	//push whatever was leftover
    	readings_merged.push(int)
    	all_interactions.push(int)
    }

  }

  all_interactions.sort(function(a,b){return a.time-b.time})
  var descriptions = []

  // Get info for how many new documents in segment
  numNew = 0
  uInt = []

  // Get array of unique opens within the segment
  for (i in opens) {
    if (opens.indexOf(opens[i]) == i) {
      uInt.push(opens[i])
    }
  }
  // Get array of unique reads in the segment
  for (i in readings_merged) {
    if (readings_merged.indexOf(readings_merged[i]) == readings_merged[i] && uInt.includes(readings_merged[i].text)) {
      uInt.push(readings_merged[i].text)
    }
  }
  // Get # of new document interactions
  for (title in uInt) {
    if (prevDocs.includes(uInt[title]) == false) {
      numNew += 1
      prevDocs.push(uInt[title])
    }
  }
  totalDocInt = uInt.length

  monthNames = ["January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December"];


  // console.log(descriptions)
  // UPDATED DESCRIPTIONS FOR LAS
  // for(var i=0; i<all_interactions.length; i++){
    // Describe the user's searches
    // First we need to get unique searches
  uSearches = []
  //remove duplicates from searches array
  for (i in searches) {
    if (searches.indexOf(searches[i]) == i) {
      uSearches.push(searches[i])
    }
  }
    if(uSearches.length == 0) {
      descriptions.push("The user made no searches.")
    }
    else if (uSearches.length == 1) {
      tempDesc = "The user searched for ";
          tempDesc += '"' + uSearches[0] + '". ';
      descriptions.push(tempDesc)
    } else {
      if (uSearches.length < 3) {
        tempDesc = "The user searched for ";
        for (let i = 0; i < uSearches.length - 1; i++) {
          tempDesc += '"' + uSearches[i] + '", ';
        }
        tempDesc += 'and "' + uSearches[uSearches.length - 1] + '".';
      } else {
        tempDesc =
          "The user made " + uSearches.length + " unique searches, including ";
        for (let i = 0; i < 2; i++) {
          tempDesc += '"' + uSearches[i] + '", ';
        }
        tempDesc += 'and "' + uSearches[2] + '".';
      }
      descriptions.push(tempDesc);
    }

    // Number of documents/new documents
    if(uInt.length == 0) {
      descriptions.push("They did not explore any documents during this time.")
    }
    else if(totalDocInt == 1) {
      tempDesc = "They "
      // If all new
      if(numNew == totalDocInt) {
        tempDesc += "explored one new document, "
      }
      // If none new
      else if(numNew==0) {
        tempDesc += "went back to one document they had previously seen, "
      }
      if (DS < 2) {
        // Document date
        tempDesc += "which was created in " + monthNames[dates[0].getMonth()] + " " + dates[0].getYear() + "."
      }
    }
    else {
      tempDesc = "They "
      // If all new
      if(numNew == totalDocInt) {
        tempDesc += "explored " + totalDocInt + " new documents, "
        if (DS < 2) {
          // Document date
          if (monthNames[dates[0].getMonth()] + " " + dates[0].getFullYear() == monthNames[dates[totalDocInt - 1].getMonth()] + " " + dates[totalDocInt - 1].getFullYear()) {
            tempDesc += "which were all created in " + monthNames[dates[0].getMonth()] + " " + dates[0].getFullYear() + "."
          }
          else {
            tempDesc += "which were created between " + monthNames[dates[0].getMonth()] + " " + dates[0].getFullYear() + " and " + monthNames[dates[totalDocInt - 1].getMonth()] + " " + dates[totalDocInt - 1].getFullYear() + "."
          }
        } else {
          tempDesc = tempDesc.slice(0,-2) + ". "
        }

      }
      // If none new
      else if(numNew==0) {
        tempDesc += "went back to " + totalDocInt + " documents they had previously seen."
        if (DS < 2) {
          // Document date
          if (monthNames[dates[0].getMonth()] + " " + dates[0].getFullYear() == monthNames[dates[totalDocInt - 1].getMonth()] + " " + dates[totalDocInt - 1].getFullYear()) {
            tempDesc += "which were all created in " + monthNames[dates[0].getMonth()] + " " + dates[0].getFullYear() + "."
          }
          else {
            tempDesc += "which were created between " + monthNames[dates[0].getMonth()] + " " + dates[0].getFullYear() + " and " + monthNames[dates[totalDocInt - 1].getMonth()] + " " + dates[totalDocInt - 1].getFullYear() + "."
          }
        }

      }
      else {
        tempDesc += "explored " + totalDocInt + " unique documents, " + numNew + " of which had not previously been read. "
        if (DS < 2) {
          // Document date
          if (monthNames[dates[0].getMonth()] + " " + dates[0].getFullYear() == monthNames[dates[totalDocInt - 1].getMonth()] + " " + dates[totalDocInt - 1].getFullYear()) {
            tempDesc += "Those documents were created in " + monthNames[dates[0].getMonth()] + " " + dates[0].getFullYear() + "."
          }
          else {
            tempDesc += "Those documents were created between " + monthNames[dates[0].getMonth()] + " " + dates[0].getFullYear() + " and " + monthNames[dates[totalDocInt - 1].getMonth()] + " " + dates[totalDocInt - 1].getFullYear() + "."
          }
        }

      }
    }

  descriptions.push(tempDesc)


  // TODO: any NER/keyword thing
  // Make NER only happen for dataset 1
  // console.log(openIDs)
  if (openIDs[0] == undefined) {
    console.error("hmm looks like theres an empty segment in this session.")
  }
  else if (openIDs[0].startsWith("armsdealing")) { 
      // Get array of unique open IDs within the segment
      // Construct list of entities with number of documents they occurred in
      peopleArr = [];
      peopleCount = [];
      geoArr = [];
      geoCount = [];
    for (const documentID of openIDs) {
        // console.log(openIDs)
        documentEntities = docs[3].find(
          (o) => o.id.toLowerCase() === documentID.toLowerCase()
        );
        peopleInDoc = documentEntities["People"];
        geosInDoc = documentEntities["Geos"];
        for (const person of peopleInDoc) {
          if (peopleArr.includes(person)) {
            peopleCount[peopleArr.indexOf(person)] += 1;
          } else {
            peopleArr.push(person);
            peopleCount.push(1);
          }
        }
        for (const geo of geosInDoc) {
          if (geoArr.includes(geo)) {
            geoCount[geoArr.indexOf(geo)] += 1;
          } else {
            geoArr.push(geo);
            geoCount.push(1);
          }
        }
      }
      // console.log("entities in segment")
      // console.log(peopleArr)
      // console.log(peopleCount)
      // console.log(geoArr)
      // console.log(geoCount)

      // Get top 3 people and top 3 geos
      topPeople = [];
      topPeopleCount = [];
      topGeos = [];
      topGeosCount = [];
      for (var i = 0; i < Math.min(2, peopleArr.length); i++) {
        maxPeople = Math.max.apply(Math, peopleCount);
        topPeopleCount.push(maxPeople);

        topPeople.push(peopleArr[peopleCount.indexOf(maxPeople)]);
        peopleCount[peopleCount.indexOf(maxPeople)] = 0;
      }

      for (var i = 0; i < Math.min(2, geoArr.length); i++) {
        maxGeos = Math.max.apply(Math, geoCount);
        topGeosCount.push(maxGeos);
        topGeos.push(geoArr[geoCount.indexOf(maxGeos)]);

        geoCount[geoCount.indexOf(maxGeos)] = 0;
      }

      tempDesc = "";
      // Push to descriptions
      if (topPeople.length == 1) {
        tempDesc +=
          "The only person referenced in the viewed documents was " +
          topPeople[0] +
          ".";
      }
      if (topPeople.length == 2) {
        tempDesc +=
          "The most referenced people in the viewed documents were " +
          topPeople[0] +
          " and " +
          topPeople[1] +
          ".";
      }
      // if (topPeople.length > 1) {
      //   tempDesc += "The most commonly referenced people in the viewed documents were " + topPeople[0]
      //   for (var i = 1; i < topPeople.length; i++) {
      //     if (i == topPeople.length-1) {
      //       tempDesc += ", and "
      //     }
      //     else {
      //       tempDesc += ", "
      //     }
      //     tempDesc += topPeople[i]
      //   }
      //
      // }
      descriptions.push(tempDesc);

      tempDesc = "";
      // Push to descriptions
      if (topGeos.length == 1) {
        tempDesc +=
          "The only location referenced in the viewed documents was " +
          topGeos[0] +
          ".";
      }
      if (topGeos.length == 2) {
        tempDesc +=
          "The most referenced locations in the viewed documents were " +
          topGeos[0] +
          " and " +
          topGeos[1] +
          ".";
      }
      descriptions.push(tempDesc);
    }

  // Average time per document
  // console.log("Length in minutes:  ")
  segLength = participantSegments[segI].length / 60
  avgLen = segLength / totalDocInt
  roundAvg = Math.round(avgLen * 100) / 100
  if(roundAvg == 1.00) {
    descriptions.push(
      "Of the " +
        totalDocInt +
        " documents open, each document recieved attention for an average of " +
        IntToTime(roundAvg * 60) +
        " minute."
    );
  } else if (roundAvg < 1.00) {
    descriptions.push(
      "Of the " +
        totalDocInt +
        " documents open, each document recieved attention for an average of " +
        IntToTime(roundAvg * 60) +
        " seconds."
    );

  }
    else {
    descriptions.push(
      "Of the " +
        totalDocInt +
        " documents open, each document recieved attention for an average of " +
        IntToTime(roundAvg * 60) +
        " minutes."
    );
  }



  // // ORIGINAL DESCRIPTIONS
  // for(var i=0; i<all_interactions.length; i++){
  //   //if many things were explored, we do not want to find pattern for all of them.
  //   if(searches.length >5 || opens.length > 15){
  //     descriptions.push("The user searched and explored many documents.")
  //     break;
  //   }else if(searches.length >3 || opens.length > 10){
  //     descriptions.push("The user searched and explored several documents.")
  //     break;
  //   }
  //
  //   try{
  //     //single search action
  //     if(all_interactions.length==1)
  //       if(all_interactions[0].interactionType=="Search")
  //         descriptions.push("The user searched for \"" + all_interactions[0].text+"\".")
  //
  //     if(all_interactions[i].interactionType=="Search"){
  //
  //       //Search->open->read pattern
  //       if(i+2 < all_interactions.length){
  //         if(all_interactions[i+1].interactionType=="Doc_open"){
  //           if(all_interactions[i+2].interactionType=="Reading"&&(all_interactions[i+1].text==all_interactions[i+2].text)){
  //             descriptions.push("The user searched for \"" + all_interactions[i].text +"\" then read " + all_interactions[i+1].text+".")
  //           }
  //         }
  //       }
  //
  //       //Search->openmany->(maybe) read pattern
  //       var docCount = 0;
  //       var finalDoc = ""
  //       for(var j=i+1; j<all_interactions.length;j++){
  //         if(all_interactions[j].interactionType=="Doc_open"){
  //           docCount++
  //         }
  //         else if(all_interactions[j].interactionType=="Reading"){
  //           finalDoc=all_interactions[j].text
  //           break
  //         }
  //         else
  //           break
  //       }
  //
  //       if(docCount==1 && finalDoc=="")
  //         descriptions.push("The user searched for \"" + all_interactions[i].text +"\" then opened " + all_interactions[i+1].text+".")
  //       else if(docCount>1 && finalDoc =="")
  //         descriptions.push("The user searched for \"" + all_interactions[i].text +"\" then opened " + docCount +" documents.")
  //       else if(docCount>1 && finalDoc !="")
  //         descriptions.push("The user searched for \"" + all_interactions[i].text +"\" then opened " + docCount +" documents before reading " + finalDoc+".")
  //
  //     }
  //   }catch{}
  //
  // }
  //
  // if(searches.length==0 && notes.length==0 && highlights.length==0 && (opens.length!=0 || readings_merged.length!=0))
  //   descriptions.push("The user focused on reading documents.")
  // else if(notes.length!=0 || highlights.length!=0)
  //   descriptions.push("The user found important information during this time.")
  // else if(opens.length > 0)
  //   descriptions.push("The user identified some documents of interest.")


  //console.log(descriptions)
  var summary = {
    interesting : (total_interactions > 0) ? true:false,
    total_interactions: total_interactions,
    all_interactions: all_interactions,

    opens: ListToCounts(opens),
    opens_list: opens,
    local_open_ratio: (total_interactions > 0) ? opens.length/total_interactions : 0,

    searches: ListToCounts(searches),
    searches_list: searches,
    local_search_ratio: (total_interactions > 0) ? searches.length/total_interactions : 0,

    notes: ListToCounts(notes),
    notes_list: notes,
    local_note_ratio: (total_interactions > 0) ? notes.length/total_interactions :0,

    highlights: ListToCounts(highlights),
    highlights_list:highlights,
    local_highlight_ratio: (total_interactions > 0) ? highlights.length/total_interactions:0,

    readings:readings_merged,
    descriptions:descriptions,

    displayedInfo: 0
  }
  return summary;
}



//Various helper stuff

function GetAllCounts(data){
  var search_count=0;
  var highlight_count=0;
  var note_count=0;
  var open_count=0;

  for(var seg of data){
    //console.log(search_count)
    search_count+=seg.searches_list.length
    highlight_count+=seg.highlights_list.length
    note_count+=seg.notes_list.length
    open_count+=seg.opens_list.length
  }

  var summary ={
    search_count:search_count,
    highlight_count:highlight_count,
    note_count:note_count,
    open_count:open_count,
    total: (search_count+highlight_count+note_count+open_count)
  }

  return summary
}

//gets counts of interaction types in segment
function TextToValue(d, type){
	var data
	switch(type){
  	case "Searches":
      data = d.searches
      break;
    case "Highlights":
      data =  d.highlights
      break;
    case "Notes":
      data =  d.notes
      break;
    case "Documents Opened":
      data =  d.opens
      break;
    case "Average":
      return d.total_interactions
      break;
  }

  var key = Object.keys(data)
  var sum = 0;
  for(var i=0; i<key.length;i++){
    sum+=data[key[i]]
  }
  return sum
}

//return specific segment from segment id, participant id, and dataset number
function GetSegment(sid, pid, dataset) {
  // console.log("getting Segment:",segments)
	for(var seg of segments){
    if (seg.sid == sid && seg.pid == pid && seg.dataset == dataset) {
      // console.log("segment Found:",seg)
			return seg
		}
	}
}

//returns all segments belonging to a participant in a specific dataset
function GetSegments(dataset,pid){
	var segments2 = []
	for(var seg of segments){
		if(seg.pid==pid && seg.dataset==dataset){
			segments2.push(seg)
		}
	}
	return segments2
}

//Given a list, convert to a dictionary of items and counts
function ListToCounts(list){
	var counts = {}

	for (var i = 0; i < list.length; i++) {
    var num = list[i];
    counts[num] = counts[num] ? counts[num] + 1 : 1;
  }
  return counts
}

//Given an int representing seconds, gives a mm:ss string back
function IntToTime(int) {
  // console.log(DS, int)
  if (DS == 4) {
    int = int /100
  }
  if (int < 3600) {
    	var min = Math.floor(int / 60);
      var sec = Math.floor(int % 60);

      if (sec.toString().length == 1) sec = "0" + sec.toString();

      return min + ":" + sec;
  } else {
    // console.log("longer than an hour!")
    var hour = Math.floor(int / 3600);
    var min = Math.floor((int - (3600 * hour)) / 60);
    if (min.toString().length == 1) min = "0" + min.toString();
    var sec = Math.floor(int % 60);
    if (sec.toString().length == 1) sec = "0" + sec.toString();
    return hour + ":" + min + ":" + sec;

  }
}

function GetInteraction(segmentID, interactionNum){
  for(var seg of data){
    if(seg.number==segmentID){
      return seg.all_interactions[interactionNum]
    }
  }
}

//Magic function found on stackoverflow for wrapping text
function wrap(text, width) {
  text.each(function () {
    var text = d3.select(this),
    words = text.text().split(/\s+/).reverse(),
    word,
    line = [],
    lineNumber = 0,
            lineHeight = 1.1, // ems
            x = text.attr("x"),
            y = text.attr("y"),
            id = text.attr("id"),
            dy = 0, //parseFloat(text.attr("dy")),
            tspan = text.text(null)
            .append("tspan")
            .attr("x", x)
            .attr("y", y)
            .attr("dy", dy + "em");
            while (word = words.pop()) {
              line.push(word);
              tspan.text(line.join(" "));
              if (tspan.node().getComputedTextLength() > width) {
                line.pop();
                tspan.text(line.join(" "));
                line = [word];
                tspan = text.append("tspan")
                .attr("x", x)
                .attr("y", y)
                .attr("dy", ++lineNumber * lineHeight + dy + "em")
                .text(word);
              }
            }
          });
}

function saveSVG(svgEl, name) {
    svgEl.setAttribute("xmlns", "http://www.w3.org/2000/svg");
    svgEl.setAttribute("xmlns:xlink", "http://www.w3.org/1999/xlink");

    var svgData = svgEl.outerHTML;
    var preface = '<?xml version="1.0" standalone="no"?>\r\n';
    var svgBlob = new Blob([preface, svgData], {type:"image/svg+xml;charset=utf-8"});
    var svgUrl = URL.createObjectURL(svgBlob);
    var downloadLink = document.createElement("a");
    downloadLink.href = svgUrl;
    downloadLink.download = name;
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
}

function saveSVGS(){
  var svgs = d3.selectAll("svg")
  svgs.attr("style","")
  //console.log(svgs._groups[0])
  for(var i=0;i<svgs._groups[0].length;i++){
    var name = "dataset"+DS+"-pid"+P+"-segment"+(i+1)+".svg"
    //saveSVG(svgs._groups[0][i], name)
    // console.log(d3.select(svgs._groups[0][i]).node())
    // console.log(i)

    try {
        var isFileSaverSupported = !!new Blob();
    } catch (e) {
        alert("blob not supported");
    }

    var html = d3.select(svgs._groups[0][i])
        .attr("title", "name")
        .attr("version", 1.1)
        .attr("xmlns", "http://www.w3.org/2000/svg")
        .node().parentNode.innerHTML;

    var blob = new Blob([html], {type: "image/svg+xml"});
    saveAs(blob, name);
  }
}
