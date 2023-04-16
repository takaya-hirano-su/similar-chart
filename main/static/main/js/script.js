// START formが変更されたらPOST
var form_market=document.getElementById("id_market");
form_market.addEventListener("change",function(){
    document.mainform.submit();
});

var form_pair=document.getElementById("id_pair");
form_pair.addEventListener("change",function(){
    document.mainform.submit();
});

var form_date=document.getElementById("id_date");
form_date.addEventListener("change",function(){
    document.mainform.submit();
});
// END formが変更されたらPOST


function drawChart(ctx,canvas,labels,datasets){
    /**
     * キャンバスにチャートを描画する関数
     */
    if(canvas){
        ctx.destroy();
    }

  
    var canvas=new Chart(ctx,{
        type:"line",
        data:{
            labels:labels,
            datasets:datasets,
        },
        options:{
            scales:{
                xAxes:[{
                    ticks:{
                        autoSkip:true,
                        maxTicksLimit:15,
                    },
                }]
            }
        }
    });
}


function getColor(index,alpha){
    /**
     * グラフの色を返す関数
     * 6色を回して返す
     */
    var color_map=[
        "rgba(255,75,0,"+String(alpha)+")",
        "rgba(0,90,255,"+String(alpha)+")",
        "rgba(3,175,122,"+String(alpha)+")",
        "rgba(77,196,255,"+String(alpha)+")",
        "rgba(246,170,0,"+String(alpha)+")",
        "rgba(255,241,0,"+String(alpha)+")",
    ];

    map_idx=index%6;

    console.log(color_map[map_idx]);

    return color_map[map_idx]
}


function drawMainChart(target_chart,similar_chart){
    /**
     * 選択したチャートとAIが選んだ似ているチャートを同時に描画する関数
     */

    var datasets=[];
    var main_ctx="main-canvas";

    //選択したチャートデータ
    datasets.push({
        data:Object.values(target_chart["close"]),
        type:"line",
        fill:false,
        label:"target-chart",
        lineTension:0.0,
        borderColor:getColor(0,0.7),
        backgroundColor:getColor(0,0.7),
    });

    //AIが選択した似ている過去チャートデータ
    var similar_num=Object.keys(similar_chart).length; 
    for(var i=0; i<similar_num; i++){
        var values=Object.values(similar_chart["No"+String(i+1)]["scaled"]["close"]);
        var dates=Object.values(similar_chart["No"+String(i+1)]["scaled"]["date"]);
        var alpha=0.3/(i+1);

        datasets.push({
            data:values,
            type:"line",
            fill:false,
            label:"similar-chart:No"+String(i+1),
            lineTension:0.0,
            borderColor:getColor(i+1,alpha),
            backgroundColor:getColor(i+1,alpha),
            pointBorderColor:"rgba(0,0,0,0)",
            pointBackgroundColor:"rgba(0,0,0,0)",
            pointRadius:0,
        });
    }

    drawChart(main_ctx,false,dates,datasets);
}


function drawSimilarChart(similar_chart){
    /**
     * AIが選択したチャートを個別に描画する関数
     */

    var similar_num=Object.keys(similar_chart).length;

    for(var i=0;i<similar_num;i++){
        var values=Object.values(similar_chart["No"+String(i+1)]["original"]["close"]);
        var dates=Object.values(similar_chart["No"+String(i+1)]["original"]["date"]);
        var canvas_id="canvas-No"+String(i+1);
        var datasets=[{
            data:values,
            type:"line",
            fill:false,
            label:"similar-chart:No"+String(i+1),
            lineTension:0.0,
            borderColor:getColor(i+1,0.7),
            backgroundColor:getColor(i+1,0.7),
            pointBorderColor:"rgba(0,0,0,0)",
            pointBackgroundColor:"rgba(0,0,0,0)",
            pointRadius:0,
        }];

        drawChart(canvas_id,false,dates,datasets);
    }
}