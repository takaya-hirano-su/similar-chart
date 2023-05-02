// marketかpairが変更されたら更新
const market_form=document.getElementById("id_market");
market_form.addEventListener("change",function(){
    document.trade_form.submit();
});

const pair_form=document.getElementById("id_pair");
pair_form.addEventListener("change",function(){
    document.trade_form.submit();
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


// START 棒グラフの描画
const pair_bar_ctx="pair-bar";
var pair_bar=new Chart(pair_bar_ctx,{
    type:"horizontalBar",
    data:{
        labels:[pair_name],
        datasets:[
            {
                label:label_crypto,
                data:[crypto_price],
                backgroundColor:getColor(1,1),
            },{
                label:label_currency,
                data:[currency],
                backgroundColor:getColor(0,1),
            }
        ]
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
// END 棒グラフの描画
