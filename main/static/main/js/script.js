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


//START キャンバスにチャートを描画
function drawChart(ctx,canvas,labels,datasets){
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
                        maxTicksLimit:20,
                    },
                }]
            }
        }
    });
}
//END


function getColor(index,alpha){
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