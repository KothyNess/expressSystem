! function($) {
    'use strict';
    var f = {
        initialized: !1,
        init: function(){
            this.initialized || (this.initialized = !0, this.mobileMenuAppear(), this.mobileMenuIcons(), this.mobileMenu(), this.mobileMenuToggle(), this.navItemActive(), this.languageToggle(), $.fn.magnificPopup && this.lightBox(), this.animatedCheckbox(), $.fn.owlCarousel && this.owlCarousel(), this.counterUp(), this.scrollToTop(), this.makeTimer(), this.lazyLoad(), this.filterLayout(), this.newsletterForm(), this.preLoader())
        },
        mobileMenuAppear: function() {
            var mobileMenu = $(".mobile-menu .mobile-menu-wrapper");

            // Adding main nav into mobile nav
            $(".main-nav").find(".navbar-nav")
            .clone(!0)
            .appendTo(mobileMenu);
        },
        mobileMenuIcons: function() {
            // Initializing mobile menu collapse button 
            $(".mobile-menu #menu").find("li").each(function() {
                $(this).find("i").remove();
                $(this).find("ul").length && $("<span/>", {
                    class: "toggle-btn"
                }).appendTo($(this).children("a"))
            })
        },
        mobileMenu: function() {
            // Preparing mobile sub menu
            $(".toggle-btn").on("click", function(t) {
                var i = $(this).closest("li"), o = i.find("ul").eq(0);
                if(i.hasClass("open")) {
                    o.slideUp(300, function() {
                        i.removeClass("open")
                    });
                } else {
                    o.slideDown(300, function() {
                        i.addClass("open");
                    });
                }
                t.stopPropagation(), t.preventDefault();
            })
        },
        mobileMenuToggle: function() {
            // Side menu toggle
            $(".mobile-menu-toggler").on("click", function(t) {
                $("body").toggleClass("menu-active"), t.preventDefault();
            }), $(".mobile-menu-overlay, .mobile-menu-close").on("click", function(t) {
                $("body").removeClass("menu-active"), t.preventDefault()
            })
        },
        navItemActive: function () {
            // Initiate Variables
            let fileName = window.location.href.split("/").reverse()[0];
            let selector = $("#menu .nav-item")

            // If window location is similar with link
            selector.each(function() {
                let anchor = $(this).find("a");
                if ($(anchor).attr("href") == fileName) {
                    anchor.addClass("active");
                }
            });

            // If any selector has active class
            selector.each(function() {
                let anchor = $(this).find("a");
                if ($(anchor).hasClass("active")) {
                    $(this).children().eq(0).addClass("active");
                }
            });

            // If no file name found
            if ("" == fileName) {
                selector.eq(0).addClass("active");
            }
        },
        stickyHeader: function() {
            var header = $(".sticky-header");
            
            // If window scroll down
            if($(window).scrollTop() >= 200) {
                header.addClass("is-sticky");
            } else {
                header.removeClass("is-sticky");
            }
        },
        languageToggle: function() {
            $(".language-button").on("click", function(e) {
                $(".language > .menu").toggle();
                e.preventDefault();
            });
        },
        lightBox: function() {
            // Youtube popup
            $(".youtube-popup").magnificPopup({
                disableOn: 300,
                type: "iframe",
                mainClass: "mfp-fade",
                removalDelay: 160,
                preloader: false,
                fixedContentPos: false
            });

            // Search popup
            $('.btn-search').magnificPopup({
                removalDelay: 500,
                callbacks: {
                    beforeOpen: function() {
                        this.st.mainClass = this.st.el.attr('data-effect');
                    }
                },
                midClick: true
            });

            // Gallery popup
            $(".popup-gallery").magnificPopup({
                delegate: "a",
                type: "image",
                tLoading: "Loading image #%curr%...",
                mainClass: "mfp-img-mobile",
                gallery: {
                    enabled: true,
                    navigateByImgClick: true,
                    preload: [0,1]
                },
                image: {
                    tError: "<a href='%url%'>The image #%curr%</a> could not be loaded."
                }
            });
        },
        animatedCheckbox: function() {
            // Initiate Variables
            var c = $("#checkboxInput");
            var s = $("#checkbox");

            s.on("click", function() {
                c.checked ? 
                s.addClass("reverse") :
                s.removeClass("reverse")
            })
        },
        owlCarousel: function() {
            var t = {
                loop: !0,
                margin: 0,
                responsiveClass: !0,
                nav: !1,
                navText: ["<i class='bx bx-chevron-left'></i>", "<i class='bx bx-chevron-right'></i>"],
                dots: !0,
                autoplay: !0,
                autoplayTimeout: !0,
                smartSpeed: 500,
                items: 1
            };

            // Home Slider
            var homeSlider = $(".home-slider");
            homeSlider.owlCarousel( $.extend(!0, {}, t, {
                nav: 1,
                autoplayHoverPause: true,
                autoplayTimeout: 6500,
                animateOut: "fadeOutLeft"
            })), homeSlider.on("changed.owl.carousel", function(event) {
                var item = event.item.index - 2;
                $(".sub-title").removeClass("animated fadeInUp");
                $("h1").removeClass("animated fadeInUp");
                $("p").removeClass("animated fadeInUp");
                $(".actions-btn").removeClass("animated fadeInUp");
                $(".owl-item").not(".cloned").eq(item).find(".sub-title").addClass("animated fadeInUp");
                $(".owl-item").not(".cloned").eq(item).find("h1").addClass("animated fadeInUp");
                $(".owl-item").not(".cloned").eq(item).find("p").addClass("animated fadeInUp");
                $(".owl-item").not(".cloned").eq(item).find(".actions-btn").addClass("animated fadeInUp");
            }),

            // Testimonial Slider
            $(".testimonial-slider").owlCarousel($.extend(!0, {}, t, {
                margin: 20,
                autoplayTimeout: 6500,
                smartSpeed: 500,
                responsiveClass: true,
                responsive: {
                    0: {
                        items: 1,
                    },

                    768: {
                        items: 2,
                    },

                    991: {
                        items: 2
                    }
                }
            }));

            $(".testimonial-slider-two").owlCarousel($.extend(!0, {}, t, {
                margin: 20,
                nav: 1,
                dots: 0,
                autoplayTimeout: 6500,
                smartSpeed: 500,
                responsiveClass: true,
                items: 1
            }));

            // Team Slider
            $(".team-slider").owlCarousel($.extend(!0, {}, t, {
                margin: 30,
                autoplayTimeout: 6500,
                smartSpeed: 500,
                responsiveClass: true,
                responsive: {
                    0: {
                        items: 1,
                    },

                    768: {
                        items: 2,
                    },

                    992: {
                        items: 3
                    }
                }
            }));

            // Service Slider
            $(".services-slider").owlCarousel($.extend(!0, {}, t, {
                margin: 30,
                center: true,
                autoplayTimeout: 6500,
                smartSpeed: 500,
                responsiveClass: true,
                responsive: {
                    0: {
                        margin: 15,
                        items: 1
                    },

                    768: {
                        items: 2
                    },

                    992: {
                        items: 3
                    }
                }
            }));
        },
        counterUp: function() {
            // Odometer
            $(".counter").counterUp({
                delay: 10,
                time: 1000
            });
        },
        scrollBtnAppear: function() {
            var goTop = $(".go-top");

            if($(window).scrollTop() >= 100) {
                goTop.addClass("active");
            } else {
                goTop.removeClass("active")
            }
        },
        scrollToTop: function() {
            $(".go-top").on("click", function(e) {
                $("html, body").animate({
                    scrollTop: 0,
                }, 500 ), e.preventDefault();
            });
        },
        makeTimer: function() {
            var endTime = new Date("December 10, 2021 17:00:00 PDT");
            var endTime = (Date.parse(endTime)) / 1000;
            var now = new Date();
            var now = (Date.parse(now) / 1000);
            var timeLeft = endTime - now;
            var days = Math.floor(timeLeft / 86400);
            var hours = Math.floor((timeLeft - (days * 86400)) / 3600);
            var minutes = Math.floor((timeLeft - (days * 86400) - (hours * 3600)) / 60);
            var seconds = Math.floor((timeLeft - (days * 86400) - (hours * 3600) - (minutes * 60)));

            if (hours < "10") {
                hours = "0" + hours;
            }
            if (minutes < "10") {
                minutes = "0" + minutes;
            }
            if (seconds < "10") {
                seconds = "0" + seconds;
            }
            
            $("#days .h1").html(days);
            $("#hours .h1").html(hours);
            $("#minutes .h1").html(minutes);
            $("#seconds .h1").html(seconds);
        },
        lazyLoad: function() {
            // Lazy Load Images
			window.lazySizesConfig = window.lazySizesConfig || {};

			window.lazySizesConfig.loadMode = 2;

            lazySizesConfig.preloadAfterLoad = true;
        },
        filterLayout: function() {
            $(".filter-grid").mixItUp({
                selectors: {
                    target: ".filter-grid-item",
                    filter: ".filter-btn"
                }
            });
        },
        newsletterForm: function() {
            var validator = $("#validator-newsletter");

            // Subscribe Form
            $("#newsletterForm").validator().on("submit", function(event) {
                if (event.isDefaultPrevented()) {
                    // Handle The Invalid Form...
                    formError();
                    submitMessage(false, "The E-mail you entered is invalid");
                } else {
                    // Everything Looks Good!
                    event.preventDefault();
                }
            });

            function callbackFunction(resp) {
                if (resp.result === "success") {
                    formSuccess();
                } else {
                    formError();
                }
            }

            function formSuccess() {
                $("#newsletterForm")[0].reset();
                submitMessage(true, "Thank you for subscribing. We have sent you a confirmation email.");
                setTimeout(function() {
                    validator.addClass("hide");
                }, 4000)
            }

            function formError() {
                $("#newsletterForm").addClass("animated shakeY");
                setTimeout(function() {
                    $("#newsletterForm").removeClass("animated shakeY");
                }, 1000)
            }

            function submitMessage(valid, msg) {
                if (valid) {
                    var msgClasses = "validation-success";
                } else {
                    var msgClasses = "validation-error";
                }
                validator.removeClass().addClass(msgClasses).text(msg);
            }

            // AJAX MailChimp
            $("#newsletterForm").ajaxChimp({
                url: "https://gmail.us1.list-manage.com/subscribe/post?u=ca9bb6a595cbcbf9728c07bfd&amp;id=c15fbaea30", // Your url MailChimp
                callback: callbackFunction
            });
        },
        preLoader: function() {
            $("#preloader")
            .delay(1000)
            .slideUp(500)
            .queue(function() {
                $(this).remove();
            });
        }
    }
    $(document).ready(function() {
        f.init();
        setInterval(function() {
            f.makeTimer()
        }, 0);
    });

    $(window).on("scroll", function() {
        f.stickyHeader(), f.scrollBtnAppear();
    });
    
}(jQuery);