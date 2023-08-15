$(document).ready(function() {
    $('#generate_salary_statement_btn').click(function(e) {

var month_name = $('#month').val()
var first_name = $('#first_name').val()
var emp_id = $('#emp_id').val()
var role = $('#role').val()
var salary = $('#Salary').val()


console.log(month_name,'month_name')
console.log(first_name,'first_name')
console.log(emp_id,'emp_id')
console.log(salary,'salary')


  $.ajax({
			   url : '/Generate_Salary_Slip_Api',
			   type : 'POST',
			   dataType: 'JSON',
			   data : {
				   month_name : month_name,
				   first_name : first_name,
				   emp_id:emp_id,
				   salary:salary,
				   role:role,

			   },
			   success: function(result) {
			   console.log(result,'portal_user_settings_msg',typeof(result))

			   }

		   })



    });
});