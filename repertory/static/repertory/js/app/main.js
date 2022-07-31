$(function(){
	
	// Requisição necessária para atualizar quantidade de notificações
	$.ajax({
		type: "GET",
		url: "/notificacoes/quantidade/",
		dataType: "json",
		success: function(notifications_count){
			if(notifications_count){
				$('#notification').html('<span class="glyphicon glyphicon-bell"></span><span class="badge">'+notifications_count+'</span>');
			} else {
				$('#notification').html('<span class="glyphicon glyphicon-bell">');
			}
		}
	});
	
	//Aqui manipulamos os componentes de abas
	$('#main-tab a[href="#last-musics"]').click(function (e) {
		// Com preventDefault anulamos a continuação do ciclo do evento no navegador
		e.preventDefault();
		$(this).tab('show');
	});
	$('#main-tab a[href="#last-repertories"]').click(function (e) {
		e.preventDefault();
		$(this).tab('show');
	});
	

	// COMPARTILHAR MÚSICA
	$('#menu #music-share-btn').click(function (e) {
		e.preventDefault();
		$('#musicAddModal #modalTitle').html('Envio de música para aprovação');
		$('#musicAddModal #messageToUserLabel').html('Para que a música seja compartilhada, antes ela precisa passar por um processo de aprovação. <b>Deseja enviar uma mensagem ao aprovador?</b>');
		$('#musicAddModal .btn-primary').html('Enviar para aprovação');
		$('#musicAddModal .btn-primary').addClass('btnSendForApprove');
		$('#workflowMusicForm').attr("action","/musicas/compartilhamento/"+$('#musicId').val()+"/");
		$('#musicAddModal').modal('show');
	});
	$('#musicAddModal').on('click', '.btnSendForApprove', function (e) {
		var formulario = $('#workflowMusicForm');
		
		var options = {
			type: formulario.attr('method'),
			data: formulario.serialize(),
			url: formulario.attr('action'),
			dataType: 'json',
			success: function(data){
				if (data.success){
					$("#panel-add #messages").noty({
						type: 'information',
						text: 'A música foi enviada para aprovação! Em breve você receberá uma resposta.',
						timeout: 10000,
					});
					// Escondemos o botão, pois a música já foi enviada para compartilhamento
					$('#music-share-btn').hide();
				}
			},
		}
		formulario.ajaxSubmit(options);	
		$('#musicAddModal').modal('hide');
	});	
	
	// APROVAR MÚSICA
	$('#menu #music-approve-btn').click(function (e) {
		e.preventDefault();
		$('#musicAddModal #modalTitle').html('Aprovação de música');
		$('#musicAddModal #messageToUserLabel').html('Deseja enviar uma mensagem ao criador da música?');
		$('#musicAddModal .btn-primary').html('Aprovar');
		$('#musicAddModal .btn-primary').addClass('btnApprove');
		$('#workflowMusicForm').attr("action","/musicas/aprovacao/"+$('#musicId').val()+"/");
		$('#musicAddModal').modal('show');
	});
	$('#musicAddModal').on('click', '.btnApprove', function (e) {
		var formulario = $('#workflowMusicForm');
		
		var options = {
			type: formulario.attr('method'),
			data: formulario.serialize(),
			url: formulario.attr('action'),
			dataType: 'json',
			success: function(data){
				if (data.success){
					$("#panel-add #messages").noty({
						type: 'success',
						text: 'A música foi aprovada e compartilhada!',
						timeout: 10000,
					});
					// Escondemos o botão, pois a música já foi enviada para compartilhamento
					$('#music-approve-btn').hide();
				}
			},
		}
		formulario.ajaxSubmit(options);	
		$('#musicAddModal').modal('hide');
	});	
	
	// SALVAR MÚSICA
	$('#menu #music-save-btn').click(function (e) {
		e.preventDefault();
		
		//Removemos todas as popovers caso exista alguma na tela
		$('.popover').hide();
		
		var formulario = $('#save-music-form');
		
		var options = {
			type: formulario.attr('method'),
			data: formulario.serialize(),
			url: formulario.attr('action'),
			enctype: formulario.attr('enctype'),
			dataType: 'json',
			//beforeSubmit: showRequest,
			success: function(data){		
				$("#panel-add #messages").noty({
					type: 'success',
					text: 'Música salva com sucesso!',
				});
				//Alteramos a action do formulário após o primeiro save por ajax
				if (data.after_create_music_id){
					formulario.attr("action","/musicas/alteracao/"+data.after_create_music_id+"/");	
				}
						
				/*AJUSTAR*/
				/*$('#music-share-btn')
					.popover({ html:true, trigger: 'manual', placement : 'bottom', title:'<b>Compartilhe sua música!</b>', content : 'Assim outros usuários também poderão vê-la!'})
					.popover('show');	*/
				/*AJUSTAR*/
				
				
			},
			statusCode: {
				400: function(data){
					var data = $.parseJSON(data.responseText);
					var all_messages = true;
											
					$.each(data, function(key,value){
						var field = value[0];
						$.each(value[1], function(key, value){
							var message = (value);
							$('input#id_'+field).popover({ trigger: "manual", placement : "right", content : message }).popover('show');
							// Tratamento diferente para widgets do plugin select2
							$('div#s2id_id_'+field).popover({ trigger: "manual", placement : "right", content : message }).popover('show');
							
							//Verifica outros tipos de erro retornados pelo Django
							if (field == "__all__"){
								$("#panel-add #messages").noty({
									type: 'error',
									text: message,
								});
								all_messages = false;
							}
								
						});
					});
					
					if(all_messages){
						$("#panel-add #messages").noty({
							type: 'error',
							text: 'Favor, verifique os campos inválidos.',
						});						
					}
				}
			}
		}
		formulario.ajaxSubmit(options);		
	});
	
	$('#notification')
		.popover({ //Aqui inicializamos o popover			
			trigger: "manual",
			placement : "bottom", //placement of the popover. also can use top, bottom, left or right
		    title : "<div id='notification-title'><h6><b>Notificações</b><h6></div>", //this is the top title bar of the popover. add some basic css
		    html: 'true', //needed to show html of course
		    content : "" //this is the content of the html box. add the image here or anything you want really.
		})
		.click(function (e) {
			var element = $(this);
			if ($(element).hasClass('popover-open')){
				$(element).popover('hide');
				$(element).removeClass('popover-open');
			} else {
				$.ajax({
					type: "GET",
					url: "/notificacoes/",
					dataType: "json",
					success: function(response){
						if (response != "") { 
							var content = "";
							$.each(response, function(i,item){
								if(item.fields.repertory){
									link = "/repertorios/"+item.fields.repertory;
								} else if (item.fields.music){
									link = "/musicas/"+item.fields.music;
								}
								content += "<div id='notification-content'><h6>" +
												"<div id='notification-date'><b>"+ item.fields.date +"</b></div>" +
						 						"<div id='notification-system-message'>"+ item.fields.systemMessage +"</div>" +
						 						"<div id='notification-user-message'><i>"+ item.fields.userMessage +"</i></div>" +
							      				"<div id='notification-link'><a href='"+ link +"'>Clique para acessar</a></div>" +
							   				"</h6></div>";
							})
						} else {
							var content = "Você não tem nenhuma notificação";
							var content = 	"<div id='notification-content'><h6>" +
	 											"<div id='notification-system-message'>Você não tem notificações.</div>" +
	 										"</h6></div>";
						}
						$(element).attr('data-content', content);
						$(element).addClass('popover-open');
						$(element).popover('show');
					}
				});
			}
			e.preventDefault();
		});

	//Adicionamos valores padrões para o plugin de notificações noty
	$.noty.defaults = {
		layout: 'bottom',
	    theme: 'montfort',
	    //type: 'alert',
	    //text: '', // can be html or string
	    dismissQueue: false, // If you want to use queue feature set this true
	    template: '<div class="noty_message"><span class="noty_text"></span><div class="noty_close"></div></div>',
	    animation: {
	        open: {height: 'toggle'},
	        close: {height: 'toggle'},
	        easing: 'swing',
	        speed: 300 // opening & closing animation speed
	    },
	    timeout: 3000, // delay for closing event. Set false for sticky notifications
	    force: false, // adds notification to the beginning of queue when set to true
	    modal: false,
	    maxVisible: 5, // you can set max visible notification for dismissQueue true option,
	    killer: false, // for close all notifications before show
	    closeWith: ['click','button'], // ['click', 'button', 'hover']
	    callback: {
	        onShow: function() {},
	        afterShow: function() {},
	        onClose: function() {},
	        afterClose: function() {}
	    },
	    buttons: false // an array of buttons
	};
	
});