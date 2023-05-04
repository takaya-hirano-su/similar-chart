function make_contents_table(){

    var link_root="/portfolio/#"
    var h_tags=["h2"];

    // 目次の親
    var contents_table=document.getElementById("contents-table");
    contents_table.textContent="目次";

    var ul_element=document.createElement("ul");
    h_tags.forEach(h_tag=>{

        // h_nタグをget
        h_list=document.getElementsByTagName(h_tag);
        
        for(var i=0;i<h_list.length;i++){
            var li_element=document.createElement("li");
            var a_element=document.createElement("a");
            a_element.textContent=h_list[i].textContent;
            a_element.setAttribute("href",link_root+String(h_list[i].id));
            
            li_element.appendChild(a_element);
            ul_element.appendChild(li_element);
        }
    });

    contents_table.appendChild(ul_element);
}


 