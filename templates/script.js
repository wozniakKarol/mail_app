$(function() {
        $('#logout').bind('click', function(){
                location.href='logout';});
});


$(function() {
        $('#new_message').bind('click', function() {
                $('#message').text('');
                $('#use').text('New message:');
                $('#popup').load("http://len.iem.pw.edu.pl/~wozniak2/templates/newmessage.html");
                return false;
        });
});


$(function() {
        $(document).on('click', '.msg', function() {
                $.getJSON($SCRIPT_ROOT + '/read_message', {
                        a: $(this).attr('id')
                }, function(data) {
                        $('#popup').text('');
                        $('#popup').append("<li> Title: "+data.message['title']+"</li>");
                        $('#unread_count').html("<button class='btn btn-primary' type="button"> Messages <span class="badge" id=unread_count>"+data.unread_count+"</span></button>");
                        $('#popup').append(data.message['content']);
                });
                return false;
        });
});
  

$(function() {
        $(document).on('click', '.delete', function() {
                $.getJSON($SCRIPT_ROOT + '/delete', {
                        a: $(this).attr('id')
                }, function(data)
                {
                        $('#use').text("");
                        $('#message').text(data.message);
                        $('#unread_count').html("<button class='btn btn-primary' type="button"> Messages <span class="badge" id=unread_count>"+data.unread_count+"</span></button>");
                        $('#popup').text("");
                });
                return false;
        });
});

$(function() {
        $('#inbox').bind('click', function() {
                $('#message').text('');
                $('#use').text('Mail');
                $('#popup').text('');
                $.getJSON($SCRIPT_ROOT + '/inbox', function(data) {
                        $.each(data.inbox, function(i, elem){
                                var user_name;
                                $.getJSON($SCRIPT_ROOT + '/get_user_name', {
                                        a: elem.from_user_id
                                }, function(user) {
                                        user_name = user.user['name'];
                                        msg=''
                                        if (elem.unread== 1) msg+="<b>";
                                        msg += "<li class='list-group-item'>From: "+user_name + " Title: " + "<a class='msg' href=# id=" + elem.message_id + ">" + elem.title + " </a>";
                                        msg += "<button  type='submit' class='delete' id='" + elem.message_id + "'>Delete</button></li>";
                                        $('#popup').append(msg);
                                });
                        });
                });
                return false;
        });
});


$(function() {
        $('#sent').bind('click', function() {
                $('#message').text('');
                $('#use').text('Send:');
                $('#popup').text('');
                $.getJSON($SCRIPT_ROOT + '/sentmessages', function(data) {
                        $.each(data.message, function(i, elem){
                                var user_name;
                                $.getJSON($SCRIPT_ROOT + '/get_user_name', {
                                        a: elem.to_user_id
                                }, function(user) {
                                        $('#popup').append("<li class='list-group-item'>To:" + user.user['name'] + " Title: <a class='msg' href=# id=" + elem.message_id + ">" + elem.title + " </a></li>");
                                });
                        });
                });
                return false;
        });
});
