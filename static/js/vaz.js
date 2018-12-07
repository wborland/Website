$(document).ready(function() {
  if(typeof intern != "undefined"){
    $('#intern').DataTable({
      "lengthMenu": [[-1, 25, 50, 100], ["All", 25, 50, 100]]
    });
  }


  $("#file-upload").change(function(){
    $("#file-name").text(this.files[0].name);
  });

    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'UA-119549461-1');
} );
