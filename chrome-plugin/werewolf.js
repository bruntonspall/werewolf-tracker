var WEREWOLF_TRACKER='http://lynchtracker.appspot.com'

function parseDate(dateString) {
    /* Today, 06:25 AM */
    /* Yesterday, 01:47 PM */
    /* 09-14-2010, 01:53 PM*/
    /* Simple case first */
    var splitDate = dateString.split(','),
        dateString = splitDate[0].trim(),
        timeString = splitDate[1].trim(),
        undef;
        
    if (dateString == 'Today') {
        date = new Date();
    } else if (dateString == 'Yesterday') {
        date = new Date();
        date.setDate(date.getDate() -1 );
    } else {
        ydm = dateString.split('-')
        date = new Date();
        date.setMonth(ydm[0]-1);
        date.setDate(ydm[1]);
        date.setYear(ydm[2]);
    }
    hour = timeString.split(':')[0]
    date.setHours(hour);
    time = timeString.split(':')[1].split(' ')[0];
    date.setMinutes(time);
    if (timeString.split(':')[1].split(' ')[1] == 'PM') {
        if (date.getHours() == 12) {
            date.setHours(12);
        } else {
            date.setHours(date.getHours() + 12);
        }
    } else {
        if (date.getHours() == 12) {
            date.setHours(0);
        }
    }
    return date;
}


var button = $('<span class="vote_button">Vote</span>');
var edit_template = "<form id=wwpoint><label for='source'>Who: </label><input name='source' id='source' type='text' placeholder='Who voted' value='{{name}}'><label for='target'>For: </label><input name='target' id='target' type='text' placeholder='Voted For' value='{{point}}'><input name='submit' type='submit' value='Submit' /></form>";

$('div.page > div > div > table > tbody> tr > td.alt2').append(button);

$('.vote_button').click(function(){
    var top = $(this).parents('.page')
    var from = top.find('.bigusername').text().trim();
    var datetime = top.find('.thead').first().text().trim()
    var point = top.find('font[color=Red]').text().trim().trim('.').trim(',');
    var date = parseDate(datetime);
    var data = {'name':from, 'datetime':date.getTime(), 'point':point, 'dtf':date};
    form = $(tim(edit_template, data));
    form.submit(function(){
        data['name']=this.source.value;
        data['point']=this.target.value;
        $.post(WEREWOLF_TRACKER+'/api/vote', data, function(response, status) {
            data['response'] = response;
            alert(tim('Submitted {{dtf}}: {{name}} point at {{point}}: {{response}}', data) );
        });
        return false;
    });
    top.append(form);
});

