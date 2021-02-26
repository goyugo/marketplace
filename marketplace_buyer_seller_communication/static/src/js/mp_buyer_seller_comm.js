/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : https://store.webkul.com/license.html/ */

odoo.define('marketplace_buyer_seller_communication.mp_buyer_seller_comm', function(require) {
    "use strict";
    // var ajax = require('web.ajax');

    $(document).ready(function(){

        $(".morempChats").slice(0, 3).show();
           if ($(".mpchatBox:hidden").length != 0) {
             $("#loadMore").show();
           }
           $("#loadMore").on('click', function (e) {
             e.preventDefault();
             // $(".morempChats:hidden").slice(0, 5).slideDown();
             $(".morempChats:hidden").slice(0,5).each(function(){
                 $(this).slideDown();
                 $(this).css("display", "flex")
             })
             if ($(".morempChats:hidden").length == 0) {
               $("#loadMore").fadeOut('slow');
             }
           });

        $('tr.mp_buyer_seller_comm_table').click(function() {
            var href = $(this).find("a").attr("href");
            if (href) {
                window.location = href;
          }
        });

        $('.comm_file_browse_btn').click(function(e){
            $('#comm_file').trigger('click');
        });

        $('input[type="file"][name="comm_file"]'). change(function(e){
            var fileName = e.target.files[0].name;
            $("#comm_file_name").text(fileName)
        });

        $('#btn_file_attach').click(function(){
            $(this).closest("form").find('.multifile').first().trigger("click")
        });

        var seq = 1

        $(document).on('click', '.remove_file', function(){
            var dlt_input_seq = $(this).closest('span').data("seq")
            $(this).closest("form").find('.multifile').each(function(){
                if($(this).data("seq") == dlt_input_seq){
                    $(this).remove();
                }
            })
            $(this).closest('span').remove();
            document.getElementById("file_attachments").value = ''
        });

        $(".multifile").change(function(e) {
            var input = document.getElementById("file_attachments");
                var div = document.getElementById("show_attachment");
            //     while (div.hasChildNodes()) {
            //         div.removeChild(div.firstChild);
            // }
            var span = document.createElement("span");
            span.setAttribute("class","mp_chat_attach")
            for (var i = 0; i < input.files.length; i++) {
                span.append(input.files[i].name)
                if(i != input.files.length-1){
                    span.append("  ,  ")
                }
            }
            span.innerHTML = $(span).text() + '&#160;' + ' <i class="fa fa-close remove_file" style="color:#191919d6;cursor:pointer;"/> ';
            $(span).attr("data-seq",seq)
            div.appendChild(span);
            $(this).closest("form").find('.multifile').first().attr("data-seq",seq)
            seq = seq+1
            $(this).closest("form").find('.multifile').first().clone().appendTo(".multi_input_file_div");
            document.getElementById("file_attachments").value = ''
            $(document.getElementById("file_attachments")).removeAttr("data-seq")
            });

        // captcha code implementation

        var math_add_ques = {
            bounds: {
                lower: 5,
                upper: 50
            },
            first: 0,
            second: 0,
            generate: function()
            {
                this.first = Math.floor(Math.random() * this.bounds.lower) + 1;
                this.second = Math.floor(Math.random() * this.bounds.upper) + 1;
            },
            show: function()
            {
                return this.first + ' + ' + this.second;
            },
            solve: function()
            {
                return this.first + this.second;
            }
        };

        $('#commModal').on('shown.bs.modal', function (e) {
            math_add_ques.generate();
            $(this).find('input[type="text"][name="mp_auth_form_input"]').prev().find(".auth_question").text(math_add_ques.show() + " : ");
        })

        $('#commModalSingle').on('shown.bs.modal', function (e) {
            math_add_ques.generate();
            $(this).find('input[type="text"][name="mp_auth_form_input"]').prev().find(".auth_question").text(math_add_ques.show() + " : ");
        })

        $(document).on('submit','form.mp_general_inquiry', function(event){
            var mp_auth_form_input = $(this).find('input[type="text"][name="mp_auth_form_input"]')
            if( mp_auth_form_input.val() != math_add_ques.solve() )
            {
                event.preventDefault()
                $(this).find(".show_form_err").css("display", "block")
            }
        });

        // Inquiry page
        $('#loadFormGeneralInquiry').load('form.mp_general_inquiry', function (e) {
            console.log("Generate Captcha / Auth Code");
            math_add_ques.generate();
            $(this).find('input[type="text"][name="mp_auth_form_input"]').prev().find(".auth_question").text(math_add_ques.show() + " : ");
        })
        
        $(document).on('submit','form.mp_general_inquiry', function(event){
            console.log("Validate Captcha / Auth Code");
            var mp_auth_form_input = $(this).find('input[type="text"][name="mp_auth_form_input"]')
            if( mp_auth_form_input.val() != math_add_ques.solve() )
            {
                event.preventDefault()
                $(this).find(".show_form_err").css("display", "block")
            }
        });

    });

});
