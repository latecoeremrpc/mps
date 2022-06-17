
    $('#delete').on('show.bs.modal', function (event) {
    var id = $(event.relatedTarget).data('id');
    var name = $(event.relatedTarget).data('name');
    $(this).find(".modal-body").text('re you sure you want to delete these division: '+name +'?');
    document.getElementById("targetlink").href="/app/division/"+id+"/delete";

    });

    $('#update').on('show.bs.modal', function (event) {
    var id = $(event.relatedTarget).data('id');
    var name = $(event.relatedTarget).data('name');
    var description = $(event.relatedTarget).data('description');
    $(this).find(".modal-body #id").val(id);
    $(this).find(".modal-body #id_name").val(name);
    $(this).find(".modal-body #id_description").val(description);

    });

