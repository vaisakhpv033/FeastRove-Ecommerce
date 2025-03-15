function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}




jQuery(document).ready(function(){
    jQuery('.status-button').on('click', function(e){
        e.preventDefault();
        var csrftoken = getCookie('csrftoken');
        let order_number = $(this).attr('data-no');
        let url = $(this).attr('data-url');
        let status = $('#'+order_number).val();

        if (!status){
            Swal.fire({
                title: "Choose a Valid status",
                icon: "error"
            })
            return false
        }
        
        Swal.fire({
            title: `Are you sure you want to update the status to ${status}`,
            icon: "info",
            showCancelButton: true,
            confirmButtonColor: "#3085d6",
            cancelButtonColor: "#d33",
            confirmButtonText: "Confirm",
        }).then((result) => {
            if (result.isConfirmed) {


                $.ajax({
                    type: 'POST',
                    url: url,
                    data:{
                        'status': status,
                        'order_number': order_number,
                        'csrfmiddlewaretoken': csrftoken, 
                    },
                    success: function (response) {
                        console.log(response);
                        if (response.status === 'Success') {
                            $('#status-'+order_number).text(response.order_status);
                            response.order_status === 'Cancelled' ? $('#status-'+order_number).removeClass("text-info text-success").addClass("text-danger") : $('#status-'+order_number).removeClass("text-info").addClass("text-success");
    
                            if ( ['Completed', 'Cancelled'].includes(response.order_status)){
                                $('#data-'+order_number).remove();                    
    
                            }else if (response.order_status === 'Accepted'){
                                $('#status-'+order_number).text(response.order_status);
                                $('#status-'+order_number).addClass("text");
                                $('#'+order_number).find('option[value="Accepted"]').text("Completed");
                                $('#'+order_number).find('option[value="Accepted"]').attr('value', 'Completed');
                            }
                        }else {
                            Swal.fire({
                                title: response.message,
                                icon: "error"
                            })
                        }
                    }
                    
                })

            }
            
        })

        
    })
    
    
})