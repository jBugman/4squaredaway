angular.module('app', ['ui.bootstrap']).config([
    '$interpolateProvider', function($interpolateProvider) {
        $interpolateProvider.startSymbol('{[{');
        $interpolateProvider.endSymbol('}]}');
    }
]).directive('eatClick', function() {
    return function(scope, element, attrs) {
        element.bind('click', function(event) {
            event.preventDefault();
        });
    }
})


function SearchResultsController($scope, $window, $http) {
    $scope.searchResults = [];
    $scope.threshold = 0;

    $scope.search = function() {
        $http.get($window.FSQ.apiUrl).then(function(response) {
            $scope.threshold = response.data['threshold'];
            $scope.searchResults = response.data['venues'].map(function(x) {
                x.marked = !$scope.isIrrelevant(x);
                return x;
            });
        });
    };

    $scope.isIrrelevant = function(venue) {
        return venue.relevance > $scope.threshold;
    };

    $scope.markedCount = function() {
        return $scope.searchResults.reduce(function(acc, x) {
            return acc + (x.marked ? 1 : 0);
        }, 0);
    };

    $scope.declension = function(number, titles) {
        return titles[(number % 100 > 4 && number % 100 < 20) ? 2 : [2, 0, 1, 1, 1, 2][(number % 10 < 5) ? number % 10 : 5]];
    };
}
