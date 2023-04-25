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
                backgroundColor:"red",
            },{
                label:label_currency,
                data:[currency],
                backgroundColor:"blue"
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
