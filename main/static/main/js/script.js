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
function drawChart(ctx,canvas,data){
    if(canvas){
        ctx.destroy();
    }

    var data_size=(Object.keys(data["pair"]).length);
    var dates=[];
    var values=[];
    for(var i=0;i<data_size;i++){
        dates.push(data["date"][i]);
        values.push(data["close"][i]);
    }

    var canvas=new Chart(ctx,{
        type:"line",
        data:{
            labels:dates,
            datasets:[{
                data:values,
                type:"line",
                fill:false,
                label:"close",
                lineTension:0.0
            }]
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