
// How to do ajax calls when I have the data.
//    $('#example').on('click', '.action-button', function() {
//        var id = $(this).data('id');
//        var action = $(this).text();
//
//        if (action === 'Action 1') {
//            // Example API call 1
//            $.ajax({
//                url: '/api/action1',
//                method: 'POST',
//                data: JSON.stringify({ id: id }),
//                contentType: 'application/json',
//                success: function(response) {
//                    console.log('Action 1 successful:', response);
//                },
//                error: function(error) {
//                    console.error('Action 1 failed:', error);
//                }
//            });
//        } else if (action === 'Action 2') {
//            // Example API call 2
//            $.ajax({
//                url: '/api/action2',
//                method: 'POST',
//                data: JSON.stringify({ id: id }),
//                contentType: 'application/json',
//                success: function(response) {
//                    console.log('Action 2 successful:', response);
//                },
//                error: function(error) {
//                    console.error('Action 2 failed:', error);
//                }
//            });
//        }
//    });
////});
//
//// ToDo: Make some unit tests for the frontend.
//

// run with: python3 -m http.server 8000
$(document).ready(function() {
    // Inline dummy data representing the data returned from API calls
    var dummyData = [
        {
            "id": 1,
            "aggregatorPlatform": "Platform 1",
            "publicationSourceUrl": "http://example.com/source1",
            "title": "Title 1",
            "category": ["Category 1", "Category 2"],
            "timestamp": "2023-01-01T00:00:00Z"
        },
        {
            "id": 2,
            "aggregatorPlatform": "Platform 2",
            "publicationSourceUrl": "http://example.com/source2",
            "title": "Title 2",
            "category": ["Category 3"],
            "timestamp": "2023-01-02T00:00:00Z"
        }
    ];

    // Initialize DataTable with dummyData
    $('#triageTable').DataTable({
        "data": dummyData,
        "columns": [
            { "data": "aggregatorPlatform", "title": "Aggregator Platform" },
            {
                "data": "publicationSourceUrl", // The "data" property should match the key in the dummyData object / the json from the API
                "title": "Source URL",
                "render": function(data) {
                    return '<a href="' + data + '">' + data + '</a>';
                }
            },
            { "data": "title", "title": "Title" },
            {
                "data": "category",
                "title": "Category",
                "render": function(data) {
                    return data.join(', ');
                }
            },
            { "data": "timestamp", "title": "Timestamp" },
            {
                "data": null,
                "title": "Actions",
                "render": function(data, type, row) {
                    return '<button class="btn btn-primary action-button" data-id="' + row.id + '">Review</button>';
                }
            }
        ]
    });

    // Handle button click event for actions
    $('#triageTable').on('click', '.action-button', function() {
        alert('Hello World');
    });
});
