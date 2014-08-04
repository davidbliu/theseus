
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
		      	var end = d.length -1;
		      	copyToClipboard(d.substring(1, end));
		      },
		      error:function (xhr, textStatus, thrownError){
		      	alert('failed');
		      }
		  });
	});
}
$(document).ready(function(){
	view_log_actions();
});