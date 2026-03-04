(function($) {
  'use strict';
  $(function() {

    function setThemeColors() {
      var selectedSidebarTheme = localStorage.getItem('selectedSidebarTheme');
      var selectedNavbarTheme = localStorage.getItem('selectedNavbarTheme');

      $body.removeClass(sidebar_classes);
      $body.addClass(selectedSidebarTheme);
      $(".sidebar-bg-options").removeClass("selected");
      $("#" + selectedSidebarTheme + "-theme").addClass("selected");

      $(".navbar").removeClass(navbar_classes);
      $(".navbar").addClass(selectedNavbarTheme);
      $(".tiles").removeClass("selected");
      $(".tiles." + selectedNavbarTheme.split(" ")[1]).addClass("selected");

      console.log("Current Sidebar Theme:", selectedSidebarTheme);
      console.log("Current Navbar Theme:", selectedNavbarTheme);
    }
    $(".nav-settings").on("click", function() {
      $("#right-sidebar").toggleClass("open");
    });
    $(".settings-close").on("click", function() {
      $("#right-sidebar,#theme-settings").removeClass("open");
    });

    $("#settings-trigger").on("click" , function(){
      $("#theme-settings").toggleClass("open");
    });


    //background constants
    var navbar_classes = "navbar-danger navbar-success navbar-warning navbar-dark navbar-light navbar-primary navbar-info navbar-pink";
    var sidebar_classes = "sidebar-light sidebar-dark";
    var $body = $("body");

    //sidebar backgrounds
    $("#sidebar-light-theme").on("click", function() {
      localStorage.setItem('selectedSidebarTheme', 'sidebar-light');
      setThemeColors();
    });

    $("#sidebar-dark-theme").on("click", function() {
      localStorage.setItem('selectedSidebarTheme', 'sidebar-dark');
      setThemeColors();
    });


    //Navbar Backgrounds
    $(".tiles.primary").on("click" , function(){
      $(".navbar").removeClass(navbar_classes);
      $(".navbar").addClass("navbar-primary");
      $(".tiles").removeClass("selected");
      $(this).addClass("selected");
      localStorage.setItem('selectedNavbarTheme', 'navbar-primary');
      setThemeColors();


    });
    $(".tiles.success").on("click" , function(){
      $(".navbar").removeClass(navbar_classes);
      $(".navbar").addClass("navbar-success");
      $(".tiles").removeClass("selected");
      $(this).addClass("selected");
      localStorage.setItem('selectedNavbarTheme', 'navbar-successy');
      setThemeColors();

    });
    $(".tiles.warning").on("click" , function(){
      $(".navbar").removeClass(navbar_classes);
      $(".navbar").addClass("navbar-warning");
      $(".tiles").removeClass("selected");
      $(this).addClass("selected");
      localStorage.setItem('selectedNavbarTheme', 'navbar-warning');
      setThemeColors();

    });
    $(".tiles.danger").on("click" , function(){
      $(".navbar").removeClass(navbar_classes);
      $(".navbar").addClass("navbar-danger");
      $(".tiles").removeClass("selected");
      $(this).addClass("selected");
      localStorage.setItem('selectedNavbarTheme', 'navbar-danger');
      setThemeColors();

    });
    $(".tiles.light").on("click" , function(){
      $(".navbar").removeClass(navbar_classes);
      $(".navbar").addClass("navbar-light");
      $(".tiles").removeClass("selected");
      $(this).addClass("selected");
      localStorage.setItem('selectedNavbarTheme', 'navbar-light');
      setThemeColors();

    });
    $(".tiles.info").on("click" , function(){
      $(".navbar").removeClass(navbar_classes);
      $(".navbar").addClass("navbar-info");
      $(".tiles").removeClass("selected");
      $(this).addClass("selected");
      localStorage.setItem('selectedNavbarTheme', 'navbar-info');
      setThemeColors();

    });
    $(".tiles.dark").on("click" , function(){
      $(".navbar").removeClass(navbar_classes);
      $(".navbar").addClass("navbar-dark");
      $(".tiles").removeClass("selected");
      $(this).addClass("selected");
      localStorage.setItem('selectedNavbarTheme', 'navbar-dark');
      setThemeColors();

    });
    $(".tiles.default").on("click" , function(){
      $(".navbar").removeClass(navbar_classes);
      $(".tiles").removeClass("selected");
      $(this).addClass("selected");
      localStorage.setItem('selectedNavbarTheme', 'navbar-primary');
      setThemeColors();

    });
    
    setThemeColors();
  });
})(jQuery);
