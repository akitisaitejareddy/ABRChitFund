/*
====================================================
 ABR CHIT FUND ERP
 Global Application JavaScript
====================================================
*/


document.addEventListener(
    "DOMContentLoaded",
    function () {



        /*
        -----------------------------------------------
        Mobile Sidebar Toggle
        -----------------------------------------------
        */


        const menuButton = document.querySelector(
            ".mobile-menu-btn"
        );


        const sidebar = document.querySelector(
            ".sidebar"
        );



        if(menuButton && sidebar){


            menuButton.addEventListener(
                "click",
                function(){


                    sidebar.classList.toggle(
                        "show"
                    );


                }
            );


        }







        /*
        -----------------------------------------------
        Auto Close Flash Messages
        -----------------------------------------------
        */


        const alerts = document.querySelectorAll(
            ".alert"
        );



        alerts.forEach(
            function(alert){


                setTimeout(
                    function(){


                        alert.classList.remove(
                            "show"
                        );


                        alert.classList.add(
                            "fade"
                        );


                    },
                    4000
                );


            }
        );







        /*
        -----------------------------------------------
        Confirm Delete Actions
        -----------------------------------------------
        */


        const deleteButtons =
            document.querySelectorAll(
                ".delete-confirm"
            );



        deleteButtons.forEach(
            function(button){


                button.addEventListener(
                    "click",
                    function(event){


                        const confirmed =
                            confirm(
                                "Are you sure you want to delete?"
                            );



                        if(!confirmed){

                            event.preventDefault();

                        }


                    }
                );


            }
        );






    }
);