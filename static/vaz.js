$(document).ready(function() {
    $('#intern').DataTable({
      "lengthMenu": [[-1, 25, 50, 100], ["All", 25, 50, 100]]
    });


    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());

    gtag('config', 'UA-119549461-1');
} );
