$(document).ready(function() {
  
  
  
  if(typeof intern != "undefined"){
    var table = $('#intern').DataTable({
      "lengthMenu": [[-1, 25, 50, 100], ["All", 25, 50, 100]]
    });
    table.order( [ 0, 'dec' ]).draw()
  }


  $("#file-upload").change(function(){
    $("#file-name").text(this.files[0].name);
  });

    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'UA-119549461-1');
} );
