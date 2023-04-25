// marketかpairが変更されたら更新
const market_form=document.getElementById("id_market");
market_form.addEventListener("change",function(){
    document.deposit_form.submit();
});

const pair_form=document.getElementById("id_currency");
pair_form.addEventListener("change",function(){
    document.deposit_form.submit();
});

const commit_button=document.getElementById("commit-button");
commit_button.addEventListener("click",function(){
    commit_form=document.getElementById("id_is_commit");
    commit_form.value="True";
});


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

    return color_map[map_idx]
}


//残高バーの描画
var datasets=[]

datasets.push({
    label:label_currency,
    data:[currency],
    backgroundColor:getColor(0,1.0),
});

var keys=Object.keys(user_coins);
for(var i=0;i<keys.length;i++){
    var key=keys[i];
    var lot=parseFloat(user_coins[key]["lot"]); //数量
    var price=lot*parseFloat(user_coins[key]["bid"]); //価格
    var name=key.toUpperCase().replace(name_currency,"");
    var label=name+" "+String(lot)+" ( "+symbol_currency+String(price)+" )";
    datasets.push({
        label:label,
        data:[price],
        backgroundColor:getColor(i+1,1.0),
    });
}      


const pair_bar_ctx="pair-bar";
var pair_bar=new Chart(pair_bar_ctx,{
    type:"horizontalBar",
    data:{
        labels:["TOTAL"],
        datasets:datasets,
    },
    options:{
        scales:{
            xAxes:[
                {
                    stacked:true,
                },
            ],
            yAxes:[
                {
                    stacked:true,
                },
            ],
        }
    }
});
