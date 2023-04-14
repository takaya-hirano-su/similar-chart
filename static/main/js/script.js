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
console.log(form_date);
console.log((form_date).length);
form_date.addEventListener("change",function(){
    document.mainform.submit();
    console.log(form_date);
});
// END formが変更されたらPOST