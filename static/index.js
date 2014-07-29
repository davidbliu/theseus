
function remove_group(group_id){
	$.ajax({
      url:'/remove',
      type: "POST",
      data: {group_id: group_id},
      success:function(d){
      	alert('success');
      	 location.reload();
      },
      error:function (xhr, textStatus, thrownError){
      	alert('failed');
      }
  });
}

function add_group(group_id, delta){
	$.ajax({
	  url:'/add_group',
	  type: "POST",
	  data: {group_id: group_id, delta: delta},
	  success:function(d){
	  	alert('success');
	  	 location.reload();
	  },
	  error:function (xhr, textStatus, thrownError){
	  	alert('failed');
	  }
  	});
}
function edit_group(group_id){
	console.log('not implemented');
}
function display_deploy_config(config){
	$("#deploy-config-window").toggle();
	$("#black-screen").toggle();
	if(config != 'none'){
		// json = config;
		//   data = JSON.parse(json);
		//   yml = YAML.stringify(data);
		$("#config").val(config);
	}
}
function copyToClipboard(text) {
  window.prompt("Copy to clipboard: Ctrl+C, Enter", text);
}
function view_log_actions(){
	$('.view-log-btn').click(function(){
		var task_id = $(this).attr('id');
		var url_string = '/get_log_url';
		$.ajax({
		      url: '/get_log_url',
		      type: "GET",
		      data: {task_id: task_id},
		      success:function(d){
		      	// var link = '<a href ="'+d+'">link to logs</a>';
		      	// $('#dialogue').dialog(d);

		      	// console.log(d);
		      	// console.log(d.length);
		      	var end = d.length -1;
		      	// console.log(d.substring(1,end));
		      	copyToClipboard(d.substring(1, end));
		      	// alert(d);
		      	// alert(link);
		      	// $('')
		      },
		      error:function (xhr, textStatus, thrownError){
		      	alert('failed');
		      }
		  });
	});
}
$(document).ready(function(){
	$('#service-input').keyup(function(e){
	    if(e.keyCode == 13)
	    {
	        var url = "/";
	        var service_param = $(this).val();
	        var label_param=$('#label-input').val();
	        if(label_param != ""){
	        	url+='?service='+service_param+'&labels='+label_param;
	        }
	        else{
	        	url+='?service='+service_param
	        }
	        window.location.href = url;

	    }
	});

	$('#label-input').keyup(function(e){
	    if(e.keyCode == 13)
	    {
	        var url = "/";
	        var label_param = $(this).val();
	        var service_param=$('#service-input').val();
	        if(service_param != ""){
	        	url+='?labels='+label_param+'&service='+service_param;
	        }
	        else{
	        	url+='?labels='+label_param
	        }
	        window.location.href = url;

	    }
	});	
	$('.remove-group-btn').click(function(){
		var group_id = $(this).parent().parent().attr('id');
		// /alert(group_id);
		var r = confirm('are you sure you want to remove this group?');
		if (r){
			remove_group(group_id);
		}
	});
	$('.plus-group-btn').click(function(){
		var group_id = $(this).parent().parent().attr('id');
		// /alert(group_id);
		var r = confirm('are you sure you want to add to group?');
		if (r){
			add_group(group_id, "1");
		}
	});
	$('.minus-group-btn').click(function(){
		var group_id = $(this).parent().parent().attr('id');
		// /alert(group_id);
		var r = confirm('are you sure you want to remove from group?');
		if (r){
			add_group(group_id, "-1");
		}
	});
	$('.edit-group-btn').click(function(){
		var group_id = $(this).parent().parent().attr('id');
		var first_child = $(this).children()[0];
		var config_data = $(first_child).text();
		// alert(config_data);
		display_deploy_config(config_data);

	});
	$(".deploy-toggle-btn").click(function(){
		display_deploy_config('none');
	});
	$("#deploy-cancel-btn").click(function(){
		display_deploy_config('none');
	});
	view_log_actions();

});