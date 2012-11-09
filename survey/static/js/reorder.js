//method that gets the PKs from the ul items and puts them in a datatype that is acceptable for POST data
function getIDs()
{
    order = $(".reorder").sortable("toArray");    
    keyArray = new Object();    
    for (i=0; i<order.length; i++)
    {
            keyArray[order[i]] = i+1;
    }    
    return keyArray;
}

$(document).ready(function(){
    //create the event handler for when the ul is sorted
    $('#sortable').sortable({
        //when updated, use ajax to update the db with new order_number values
        update: function(event, ui){
            $.ajax({
                type: "POST",
                data: getIDs(),
                success: function(data){}
            })
        }
    });
    
    $( "#sortable" ).disableSelection();
});

