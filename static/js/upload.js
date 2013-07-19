var holder = $("#holder"),
    tests = {
      filereader: typeof FileReader != 'undefined',
      dnd: 'draggable' in document.createElement('span'),
      formdata: !!window.FormData,
      progress: "upload" in new XMLHttpRequest
    }, 
    support = {
      filereader: document.getElementById('filereader'),
      formdata: document.getElementById('formdata'),
      progress: document.getElementById('progress')
    },
    acceptedTypes = {
      'image/png': true,
      'image/jpeg': true,
      'image/gif': true
    },
    notices = {
      all      : $(".notice"), 
      drag     : $("#drag-notice"), 
      drop     : $("#drop-notice"), 
      multi    : $("#multi-notice"), 
      hideall  : function() {
        this.all.removeClass("show");
      }, 
      use      : function(name) {
        this.hideall();
        this[name].addClass("show");
      }
    },
    progressLayout = $("#progress"), 
    progress = $("#uploadprogress"),
    fileupload = $("#upload"), 
    arrow = $("#arrow"), 
    card = $("#card"), 
    _TYPE_ICON_SRC = {
      video  : "/static/img/video.png", 
      audio  : "/static/img/audio.png", 
      binary : "/static/img/binary.png", 
      pdf    : "/static/img/pdf.png"
    }, 
    image_card = $("#image-card"), 
    image_preview = $("#image-preview"), 
    $window = $(window)
    zoomed = false;

"filereader formdata progress".split(' ').forEach(function (api) {
  if (tests[api] === false) {
    console.log(api + " not supported!");
  }
});


function previewfile(file) {
  if (tests.filereader === true && acceptedTypes[file.type] === true) {
    var reader = new FileReader();
    reader.onload = function (event) {
      var image = new Image();
      image.src = event.target.result;
      image.width = 250; // a fake resize
      holder.appendChild(image);
    };

    reader.readAsDataURL(file);
  }  else {
    holder.innerHTML = '<p>Uploaded ' + file.name + ' ' + (file.size ? (file.size/1024|0) + 'K' : '');
  }
}

function showCard(r) {
    var filename = $("#filename");
    var filesize = $("#filesize");
    var uploadtime = $("#uploadtime");
    var link_s = $("#link_s");
    var file_icon = $(".file-icon");
    var icon = $(".file-icon > img");
    var play_button = $("#play-link");
    var download_button = $("#download-link");
    var image_link = $("#image-link");
    var image_link_input = $("#image-link input");
    var image;
    var element;

    console.log(history.pushState("what", "p", r.url_p));

    if(r.type === "image") {
        element = new Image();
        element.src = r.url_i;
        image_link.before(element);
        file_icon.addClass("invisible");
        image_card.addClass("show-card");
        progressLayout.removeClass("show");
        holder.remove();
        image = $("#image-preview img");
        image.click(zoom);
        image_link_input.val(r.url_s);
        return;
    }

    filename.text(r.filename);
    filesize.text(r.size);
    uploadtime.text(r.time);
    link_s.val(r.url_s);
    icon.attr("src", _TYPE_ICON_SRC[r.type]);

    if(r.type === "binary") {
        play_button.hide();
    }else if(r.type == "pdf") {
        play_button.text("preview");
        play_button.attr("href", r.url_i);
    }else{
        play_button.attr("href", r.url_i);
    }
    download_button.attr("href", r.url_d);
    
    console.log(card.height(), card.width());

    holder.remove();
    progressLayout.removeClass("show");
    arrow.addClass("hide");
    card.addClass("show-card");
}

function readfiles(files) {
    if(files.length != 1) {
      // multi file
      notices.use("multi");
      setTimeout(function() {
        notices.use("drag");
      }, 1000);
      return false;
    }
    var formData = tests.formdata ? new FormData() : null;
    for (var i = 0; i < files.length; i++) {
      if (tests.formdata) formData.append('file', files[i]);
      //previewfile(files[i]);
    }

    // now post a new XHR request
    if (tests.formdata) {
      var xhr = new XMLHttpRequest();
      xhr.open('POST', '/');
      xhr.onreadystatechange = function() {
        if (xhr.readyState==4){
            if(xhr.status==200){
                //window.location.href = xhr.responseText;
                progress.value = progress.innerHTML = 100;
                showCard(JSON.parse(xhr.responseText));
            }
            else{
                alert("上传失败，请确认上传的文件类型合法" );
                progress.value = progress.innerHTML = 0;
            }
        }
      };

      if (tests.progress) {
        notices.hideall();
        arrow.addClass("hide");
        progressLayout.addClass("show");
        xhr.upload.onprogress = function (event) {
          if (event.lengthComputable) {
            var complete = (event.loaded / event.total * 100 | 0);
            progress.val(complete);
            progress.text(complete);
          }
        }
      }

      xhr.send(formData);
    }
}

if (tests.dnd) { 
  holder.on('dragover', function () {
      arrow.addClass("hover"); 
      notices.use("drop"); 
      return false; 
  });
  holder.on('dragend', function () { 
      arrow.removeClass("hover"); 
      notices.use("drag"); 
      return false; 
  });
  holder.on('dragleave', function () { 
      arrow.removeClass("hover"); 
      notices.use("drag"); 
      return false; 
  });
  holder.on('drop', function (e) {
    holder.removeClass();
    e.originalEvent.preventDefault();
    readfiles(e.originalEvent.dataTransfer.files);
  });
} else {
  fileupload.className = 'hidden';
  fileupload.querySelector('input').onchange = function () {
    readfiles(this.files);
  };
}

function zoom() {
    if(!zoomed) {
        var height = $window.height();
        image_preview.addClass("zoomed");
        image_preview.css("max-height", height * 0.7);
        zoomed = true;
    }else{
        image_preview.removeClass("zoomed");
        image_preview.css("max-height", "");
        zoomed = false;
    }
}

$window.resize(function() {
    var height = $window.height();
    if(zoomed) {
        image_preview.css("max-height", height * 0.7);
    }
});

