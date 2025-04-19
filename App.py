import json
import math
import sys
from abc import ABC, abstractmethod
import os
import folium
from folium import IFrame
from folium.plugins import PolyLineTextPath, MousePosition
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QMainWindow,
    QHBoxLayout,
    QListWidget,
    QLineEdit,
    QDialog,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QDialogButtonBox,
    QCheckBox,
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QUrl


class DistanceCalculator:
    @staticmethod
    def calculate_distance(lat1, lon1, lat2, lon2):
        R = 6371
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        latdiff = lat2 - lat1
        londiff = lon2 - lon1
        a = (
            math.sin(latdiff / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(londiff / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c


class Location:
    def __init__(self, latitude, longitude):
        self.__latitude = latitude
        self.__longitude = longitude

    def get_latitude(self):
        return self.__latitude

    def get_longitude(self):
        return self.__longitude

    def set_latitude(self, latitude):
        self.__latitude = latitude

    def set_longitude(self, longitude):
        self.__longitude = longitude


class Stop:
    def __init__(self, stopid, name, type, location, son_durak, nextStops, transfers):
        self.__stopid = stopid
        self.__name = name
        self.__type = type
        self.__location = location
        self.__son_durak = son_durak
        self.__nextStops = nextStops
        self.__transfers = transfers

    def get_stopid(self):
        return self.__stopid

    def get_name(self):
        return self.__name

    def get_type(self):
        return self.__type

    def get_location(self):
        return self.__location

    def get_son_durak(self):
        return self.__son_durak

    def get_nextStops(self):
        return self.__nextStops

    def get_transfers(self):
        return self.__transfers

    def set_stopid(self, stopid):
        self.__stopid = stopid

    def set_name(self, name):
        self.__name = name

    def set_type(self, type):
        self.__type = type

    def set_location(self, location):
        self.__location = location

    def set_son_durak(self, son_durak):
        self.__son_durak = son_durak

    def set_nextStops(self, nextStops):
        self.__nextStops = nextStops

    def set_transfers(self, transfers):
        self.__transfers = transfers


class Transfer:
    def __init__(self, transferStopId, sure, ucret):
        self.__transferStopId = transferStopId
        self.__sure = sure
        self.__ucret = ucret

    def get_transferStopId(self):
        return self.__transferStopId

    def get_sure(self):
        return self.__sure

    def get_ucret(self):
        return self.__ucret

    def set_transferStopId(self, transferStopId):
        self.__transferStopId = transferStopId

    def set_sure(self, sure):
        self.__sure = sure

    def set_ucret(self, ucret):
        self.__ucret = ucret


class Distance_Based_Fare(ABC):
    @abstractmethod
    def calculate_fare(self, distance):
        pass

    @abstractmethod
    def set_fees(self, json_file):
        pass


class Fixed_Fare(ABC):
    @abstractmethod
    def returnIconPath(self):
        pass


class Vehicle(ABC):
    def __init__(self, markerGroup):
        self.markerGroup = markerGroup

    @abstractmethod
    def returnMarkerGroup(self):
        pass


class Bus(Vehicle, Fixed_Fare):
    def __init__(self, busIconFileName, busMarkerGroup):
        super().__init__(busMarkerGroup)
        self.busIconFileName = busIconFileName
        self.busIconPath = os.path.join(os.getcwd(), busIconFileName)
        self.linecolor = "green"
        self.isTiedToGoverment = True

    def returnMarkerGroup(self):
        return self.markerGroup

    def returnIconPath(self):
        return self.busIconPath


class Tram(Vehicle, Fixed_Fare):
    def __init__(self, tramIconFileName, tramMarkerGroup):
        super().__init__(tramMarkerGroup)
        self.tramIconFileName = tramIconFileName
        self.tramIconPath = os.path.join(os.getcwd(), tramIconFileName)
        self.linecolor = "darkred"
        self.isTiedToGoverment = True

    def returnMarkerGroup(self):
        return self.markerGroup

    def returnIconPath(self):
        return self.tramIconPath


class Taxi(Vehicle, Distance_Based_Fare):

    def __init__(self, opening_fee, cost_per_km, taxiMarkerGroup):
        self.opening_fee = opening_fee
        self.cost_per_km = cost_per_km
        self.speed = 70
        self.linecolor = "yellow"
        super().__init__(taxiMarkerGroup)
        self.tiedToGoverment = False

    def setMarkerGroup(self, tMarker):
        self.markerGroup = tMarker

    def returnMarkerGroup(self):
        return self.markerGroup

    def calculate_fare(self, distance):
        return self.opening_fee + (distance * self.cost_per_km)

    def calculate_taxi_time(self, distance):
        time_by_hour = distance / self.speed
        time_by_minute = time_by_hour * 60
        return time_by_minute

    def set_fees(self, json_file):
        with open(json_file, "r", encoding="utf-8") as file:
            data = json.load(file)
            if "taxi" not in data:
                raise ValueError("'taxi' anahtarı bulunamadı!")
            self.opening_fee = data["taxi"]["openingFee"]
            self.cost_per_km = data["taxi"]["costPerKm"]


class Passenger(ABC):
    def __init__(
        self,
        passenger_type,
        passengerLocation,
        passengerTargetLocation,
        creditCards=None,
        cash_cards=None,
        kent_cards=None,
        is_special_day=False,
    ):
        self.__passenger_type = passenger_type
        self.__passengerLocation = passengerLocation
        self.__passengerTargetLocation = passengerTargetLocation
        self.__creditCards = creditCards if creditCards else []
        self.__cash_cards = cash_cards if cash_cards else []
        self.__kent_cards = kent_cards if kent_cards else []
        self.__walkingSpeed = 5
        self.__is_special_day = is_special_day

    def get_passenger_type(self):
        return self.__passenger_type

    def get_passengerLocation(self):
        return self.__passengerLocation

    def get_passengerTargetLocation(self):
        return self.__passengerTargetLocation

    def get_creditCards(self):
        return self.__creditCards

    def get_cash_cards(self):
        return self.__cash_cards

    def get_kent_cards(self):
        return self.__kent_cards

    def get_walkingSpeed(self):
        return self.__walkingSpeed

    def set_passengerLocation(self, location):
        self.__passengerLocation = location

    def set_passengerTargetLocation(self, location):
        self.__passengerTargetLocation = location

    def set_creditCards(self, creditCards):
        self.__creditCards = creditCards

    def set_cash_cards(self, cash_cards):
        self.__cash_cards = cash_cards

    def set_kent_cards(self, kent_cards):
        self.__kent_cards = kent_cards

    def set_walkingSpeed(self, walkingSpeed):
        self.__walkingSpeed = walkingSpeed

    @abstractmethod
    def get_discount(self, fare):
        pass

    def calculate_walking_time(self, distance):
        return distance / self.__walkingSpeed

    def get_is_special_day(self):
        return self.__is_special_day

    def set_is_special_day(self, is_special_day):
        self.__is_special_day = is_special_day

    def get_creditCard_Money_Amount(self):
        balance = 0
        if self.__creditCards is not None:
            for card in self.__creditCards:
                balance += card.balance
        return balance

    def get_cash_Money_Amount(self):
        balance = 0
        if self.__cash_cards is not None:
            for card in self.__cash_cards:
                balance += card.balance
        return balance

    def get_kentCard_Money_Amount(self):
        balance = 0
        if self.__kent_cards is not None:
            for card in self.__kent_cards:
                balance += card.balance
        return balance

    def can_pay(self, amount):
        total_balance = (
            self.get_cash_Money_Amount()
            + self.get_creditCard_Money_Amount()
            + self.get_kentCard_Money_Amount()
        )
        return total_balance >= amount


class General(Passenger):
    def __init__(
        self,
        passenger_type,
        passengerLocation,
        passengerTargetLocation,
        creditCards=None,
        cash_cards=None,
        kent_cards=None,
        is_special_day=False,
    ):
        super().__init__(
            "Genel",
            passengerLocation,
            passengerTargetLocation,
            creditCards,
            cash_cards,
            kent_cards,
            is_special_day,
        )

    def get_discount(self, fare):
        return fare


class Student(Passenger):
    def __init__(
        self,
        passenger_type,
        passengerLocation,
        passengerTargetLocation,
        creditCards=None,
        cash_cards=None,
        kent_cards=None,
        is_special_day=False,
    ):
        super().__init__(
            "Öğrenci",
            passengerLocation,
            passengerTargetLocation,
            creditCards,
            cash_cards,
            kent_cards,
            is_special_day,
        )

    def get_discount(self, fare):
        return fare * 0.5


class Elderly(Passenger):
    def __init__(
        self,
        passenger_type,
        passengerLocation,
        passengerTargetLocation,
        creditCards=None,
        cash_cards=None,
        kent_cards=None,
        is_special_day=False,
    ):
        super().__init__(
            "Yaşlı",
            passengerLocation,
            passengerTargetLocation,
            creditCards,
            cash_cards,
            kent_cards,
            is_special_day,
        )

    def get_discount(self, fare):
        return 0


class PaymentType(ABC):
    def __init__(self, balance):
        self.balance = balance

    @abstractmethod
    def pay(self, fare):
        pass


class KrediKarti(PaymentType):
    def __init__(self, balance):
        super().__init__(balance)

    def pay(self, fare):
        if self.balance >= fare:
            return True
        return False


class Nakit(PaymentType):
    def __init__(self, balance):
        super().__init__(balance)

    def pay(self, fare):
        if self.balance >= fare:
            return True
        return False


class KentKart(PaymentType):
    def __init__(self, balance):
        super().__init__(balance)

    def pay(self, fare):
        if self.balance >= fare:
            return True
        return False


class StopLoader:
    @staticmethod
    def load_stops_from_json(json_file):
        with open(json_file, "r", encoding="utf-8") as file:
            data = json.load(file)
            if "duraklar" not in data:
                raise ValueError("'duraklar' anahtarı bulunamadı!")
            stops = []

            for stop_data in data["duraklar"]:
                transfers = stop_data.get("transfer", None)
                if transfers:
                    transfers = Transfer(
                        transferStopId=transfers["transferStopId"],
                        sure=transfers["transferSure"],
                        ucret=transfers["transferUcret"],
                    )
                stopToAppend = Stop(
                    stopid=stop_data["id"],
                    name=stop_data["name"],
                    type=stop_data["type"],
                    location=Location(stop_data["lat"], stop_data["lon"]),
                    son_durak=stop_data["sonDurak"],
                    nextStops=stop_data.get("nextStops", []),
                    transfers=transfers,
                )
                stops.append(stopToAppend)
            return {stop.get_stopid(): stop for stop in stops}


class RouteLogic(ABC):
    @abstractmethod
    def calculateRoute(
        self, stops, initial_stop, target_stop, user: Passenger, vehicle_bias
    ):
        pass


class bellmanFord_Standard(RouteLogic):
    def calculateRoute(
        self,
        stops,
        initial_stop,
        target_stop,
        user: Passenger,
        vehicle_bias,
        visited=None,
    ):
        if visited is None:
            visited = set()

        relaxation_amount = len(stops) - 1
        relaxation_counter = 0
        distances = {stop: float("inf") for stop in stops.values()}
        distances[initial_stop] = 0
        path_dictionary = {stop: None for stop in stops.values()}
        relaxation_bool = True

        while relaxation_bool:
            relaxation_bool = False
            for stop in stops.values():
                for next_stop in stop.get_nextStops():
                    next_stop_id = next_stop["stopId"]
                    next_stop_object = stops[next_stop_id]
                    if user.get_is_special_day() and next_stop_object.get_type() in [
                        "bus",
                        "tram",
                    ]:
                        score = next_stop["mesafe"] * 0.1 + next_stop["sure"] * 0.5
                    else:
                        score = (
                            next_stop["mesafe"] * 0.1
                            + next_stop["sure"] * 0.5
                            + user.get_discount(next_stop["ucret"]) * 0.4
                        )
                    if next_stop_object.get_type() == vehicle_bias:
                        score *= 0.01
                    if distances[stop] + score < distances[next_stop_object]:
                        distances[next_stop_object] = distances[stop] + score
                        path_dictionary[next_stop_object] = stop
                        relaxation_counter += 1
                        relaxation_bool = True
                if stop.get_transfers():
                    transfer_stop_id = stop.get_transfers().get_transferStopId()
                    transfer_stop_data = stops[transfer_stop_id]
                    if user.get_is_special_day() and transfer_stop_data.get_type() in [
                        "bus",
                        "tram",
                    ]:
                        score = stop.get_transfers().get_sure() * 0.5
                    else:
                        score = (
                            stop.get_transfers().get_sure() * 0.5
                            + user.get_discount(stop.get_transfers().get_ucret()) * 0.4
                        )
                    if stops[transfer_stop_id].get_type() == vehicle_bias:
                        score *= 0.01
                    if distances[stop] + score < distances[transfer_stop_data]:
                        distances[transfer_stop_data] = distances[stop] + score
                        path_dictionary[transfer_stop_data] = stop
                        relaxation_counter += 1
                        relaxation_bool = True

            if not relaxation_bool:
                break
            if relaxation_counter > relaxation_amount * 2:
                raise RuntimeError("Negatif döngü bulundu, uygulama sonlandırılıyor")

        if all(
            dist == float("inf")
            for stop, dist in distances.items()
            if stop != initial_stop
        ):
            closestToInitialStop = min(
                [stop for stop in stops.values() if stop not in visited],
                key=lambda stop: DistanceCalculator.calculate_distance(
                    initial_stop.get_location().get_latitude(),
                    initial_stop.get_location().get_longitude(),
                    stop.get_location().get_latitude(),
                    stop.get_location().get_longitude(),
                ),
            )
            visited.add(closestToInitialStop)
            return self.calculateRoute(
                stops, closestToInitialStop, target_stop, user, vehicle_bias, visited
            )
        elif distances[target_stop] == float("inf"):
            closestToTargetStop = min(
                [stop for stop in stops.values() if stop not in visited],
                key=lambda stop: DistanceCalculator.calculate_distance(
                    target_stop.get_location().get_latitude(),
                    target_stop.get_location().get_longitude(),
                    stop.get_location().get_latitude(),
                    stop.get_location().get_longitude(),
                ),
            )
            visited.add(closestToTargetStop)
            return self.calculateRoute(
                stops, initial_stop, closestToTargetStop, user, vehicle_bias, visited
            )

        path_to_target = []
        current_stop = target_stop
        total_time = 0
        total_distance = 0
        total_price = 0
        transfer_count = 0

        while current_stop is not None:
            path_to_target.insert(0, current_stop)
            if path_dictionary[current_stop] is not None:
                prev_stop = path_dictionary[current_stop]
                for next_stop in prev_stop.get_nextStops():
                    if next_stop["stopId"] == current_stop.get_stopid():
                        total_time += next_stop["sure"]
                        total_distance += next_stop["mesafe"]
                        if not (
                            user.get_is_special_day()
                            and current_stop.get_type() in ["bus", "tram"]
                        ):
                            total_price += next_stop["ucret"]
                        break
                if (
                    prev_stop.get_transfers()
                    and prev_stop.get_transfers().get_transferStopId()
                    == current_stop.get_stopid()
                ):
                    total_time += prev_stop.get_transfers().get_sure()
                    if not (
                        user.get_is_special_day()
                        and current_stop.get_type() in ["bus", "tram"]
                    ):
                        total_price += prev_stop.get_transfers().get_ucret()
                    transfer_count += 1
            current_stop = path_dictionary[current_stop]

        total_price = user.get_discount(total_price)
        if total_price > transfer_count:
            total_price -= transfer_count
        else:
            total_price = 0

        routeObj = RouteInfo(
            path_to_target,
            total_time,
            total_distance,
            total_price,
            "",
            vehicle_bias,
            self,
        )
        return routeObj


class bellmanFord_LeastStops(RouteLogic):
    def calculateRoute(
        self,
        stops,
        initial_stop,
        target_stop,
        user: Passenger,
        vehicle_bias,
        visited=None,
    ):
        if visited is None:
            visited = set()
        path_dictionary = {stop: None for stop in stops.values()}
        stops_count = {stop: float("inf") for stop in stops.values()}
        stops_count[initial_stop] = 0
        relaxation_bool = True

        while relaxation_bool:
            relaxation_bool = False
            for stop in stops.values():
                for next_stop in stop.get_nextStops():
                    next_stop_id = next_stop["stopId"]
                    next_stop_object = stops[next_stop_id]
                    if stops_count[stop] + 1 < stops_count[next_stop_object]:
                        stops_count[next_stop_object] = stops_count[stop] + 1
                        relaxation_bool = True
                        path_dictionary[next_stop_object] = stop
                if stop.get_transfers():
                    transfer_stop_id = stop.get_transfers().get_transferStopId()
                    transfer_stop_data = stops[transfer_stop_id]
                    if stops_count[stop] + 1 < stops_count[transfer_stop_data]:
                        stops_count[transfer_stop_data] = stops_count[stop] + 1
                        relaxation_bool = True
                        path_dictionary[transfer_stop_data] = stop
            if not relaxation_bool:
                break

        if all(
            dist == float("inf")
            for stop, dist in stops_count.items()
            if stop != initial_stop
        ):
            closestToInitialStop = min(
                [stop for stop in stops.values() if stop not in visited],
                key=lambda stop: DistanceCalculator.calculate_distance(
                    initial_stop.get_location().get_latitude(),
                    initial_stop.get_location().get_longitude(),
                    stop.get_location().get_latitude(),
                    stop.get_location().get_longitude(),
                ),
            )
            visited.add(closestToInitialStop)
            return self.calculateRoute(
                stops, closestToInitialStop, target_stop, user, vehicle_bias, visited
            )
        elif stops_count[target_stop] == float("inf"):
            closestToTargetStop = min(
                [stop for stop in stops.values() if stop not in visited],
                key=lambda stop: DistanceCalculator.calculate_distance(
                    target_stop.get_location().get_latitude(),
                    target_stop.get_location().get_longitude(),
                    stop.get_location().get_latitude(),
                    stop.get_location().get_longitude(),
                ),
            )
            visited.add(closestToTargetStop)
            return self.calculateRoute(
                stops, initial_stop, closestToTargetStop, user, vehicle_bias, visited
            )

        path_to_target = []
        current_stop = target_stop
        total_time = 0
        total_distance = 0
        total_price = 0
        transfer_count = 0

        while current_stop is not None:
            path_to_target.insert(0, current_stop)
            if path_dictionary[current_stop] is not None:
                prev_stop = path_dictionary[current_stop]
                for next_stop in prev_stop.get_nextStops():
                    if next_stop["stopId"] == current_stop.get_stopid():
                        total_time += next_stop["sure"]
                        total_distance += next_stop["mesafe"]
                        if not (
                            user.get_is_special_day()
                            and current_stop.get_type() in ["bus", "tram"]
                        ):
                            total_price += next_stop["ucret"]
                        break
                if (
                    prev_stop.get_transfers()
                    and prev_stop.get_transfers().get_transferStopId()
                    == current_stop.get_stopid()
                ):
                    total_time += prev_stop.get_transfers().get_sure()
                    if not (
                        user.get_is_special_day()
                        and current_stop.get_type() in ["bus", "tram"]
                    ):
                        total_price += prev_stop.get_transfers().get_ucret()
                    transfer_count += 1
            current_stop = path_dictionary[current_stop]

        total_price = user.get_discount(total_price)
        if total_price > transfer_count:
            total_price -= transfer_count
        else:
            total_price = 0

        routeObj = RouteInfo(
            path_to_target,
            total_time,
            total_distance,
            total_price,
            "",
            vehicle_bias,
            self,
        )
        return routeObj


class RoutePlanner:
    def __init__(self, stops, vehicles, distance_calculator):
        self.stops = stops
        self.vehicles = vehicles
        self.distance_calculator = distance_calculator

    def find_nearest_stop(self, location):
        return min(
            self.stops.values(),
            key=lambda stop: self.distance_calculator.calculate_distance(
                location.get_latitude(),
                location.get_longitude(),
                stop.get_location().get_latitude(),
                stop.get_location().get_longitude(),
            ),
        )

    def finalize_routes(
        self,
        user: Passenger,
        target_location,
        vehicle_bias,
        route_logic: RouteLogic,
        routeName,
    ):

        initial_closest_stop = self.find_nearest_stop(user.get_passengerLocation())
        initial_target_stop = self.find_nearest_stop(target_location)

        route_obj = route_logic.calculateRoute(
            self.stops, initial_closest_stop, initial_target_stop, user, vehicle_bias
        )
        if not route_obj.get_route():
            return route_obj  # Taxi icin

        final_closest_stop = route_obj.get_route()[0]
        final_target_stop = route_obj.get_route()[-1]

        distance_to_closest_stop = self.distance_calculator.calculate_distance(
            user.get_passengerLocation().get_latitude(),
            user.get_passengerLocation().get_longitude(),
            final_closest_stop.get_location().get_latitude(),
            final_closest_stop.get_location().get_longitude(),
        )

        taxi_price = 0
        taxi_time = 0
        walking_time = 0

        if distance_to_closest_stop > 3:
            taxi_price = self.vehicles["taxi"].calculate_fare(distance_to_closest_stop)
            taxi_time = self.vehicles["taxi"].calculate_taxi_time(
                distance_to_closest_stop
            )
        else:
            walking_time = user.calculate_walking_time(distance_to_closest_stop)

        target_stop_distance = self.distance_calculator.calculate_distance(
            target_location.get_latitude(),
            target_location.get_longitude(),
            final_target_stop.get_location().get_latitude(),
            final_target_stop.get_location().get_longitude(),
        )

        if target_stop_distance > 3:
            taxi_price += self.vehicles["taxi"].calculate_fare(target_stop_distance)
            taxi_time += self.vehicles["taxi"].calculate_taxi_time(target_stop_distance)
        else:
            walking_time += user.calculate_walking_time(target_stop_distance)

        route_obj.set_taxi_price(taxi_price)
        route_obj.set_price(route_obj.get_price() + taxi_price)
        route_obj.set_time(route_obj.get_time() + taxi_time + walking_time)
        route_obj.set_routeName(routeName)
        route_obj.set_distance(
            route_obj.get_distance() + target_stop_distance + distance_to_closest_stop
        )
        return route_obj


class TaxiRouteLogic(RouteLogic):
    def __init__(self, taxi: Taxi):
        self.__taxi = taxi

    def calculateRoute(
        self, stops, initial_stop, target_stop, user: Passenger, vehicle_bias
    ):

        distance = DistanceCalculator.calculate_distance(
            user.get_passengerLocation().get_latitude(),
            user.get_passengerLocation().get_longitude(),
            user.get_passengerTargetLocation().get_latitude(),
            user.get_passengerTargetLocation().get_longitude(),
        )

        if distance < 3:
            route_info = RouteInfo(
                route=[],
                time=user.calculate_walking_time(distance),
                distance=distance,
                price=0,
                routeName="🚶Yürüme Rotasi🚶",
                vehicleBias=None,
                routeLogic=self,
            )
            return route_info

        taxi_fare = 0

        taxi_fare = self.__taxi.calculate_fare(distance)

        taxi_time = self.__taxi.calculate_taxi_time(distance)

        route_info = RouteInfo(
            route=[],
            time=taxi_time,
            distance=distance,
            price=taxi_fare,
            routeName="🚕Sadece taksi ile rota🚕",
            vehicleBias="taxi",
            routeLogic=self,
        )
        return route_info


class RouteInfo:
    def __init__(
        self,
        route,
        time,
        distance,
        price,
        routeName,
        vehicleBias,
        routeLogic: RouteLogic,
    ):
        self.__route = route
        self.__time = time
        self.__distance = distance
        self.__price = price
        self.__taxi_price = 0
        self.__routeName = routeName
        self.__vehicleBias = vehicleBias
        self.__routeLogic = routeLogic

    def get_route(self):
        return self.__route

    def get_time(self):
        return self.__time

    def get_distance(self):
        return self.__distance

    def get_price(self):
        return self.__price

    def get_taxi_price(self):
        return self.__taxi_price

    def get_routeName(self):
        return self.__routeName

    def get_vehicleBias(self):
        return self.__vehicleBias

    def get_routeLogic(self):
        return self.__routeLogic

    def set_route(self, route):
        self.__route = route

    def set_time(self, time):
        self.__time = time

    def set_distance(self, distance):
        self.__distance = distance

    def set_price(self, price):
        self.__price = price

    def set_taxi_price(self, taxi_price):
        self.__taxi_price = taxi_price

    def set_routeName(self, routeName):
        self.__routeName = routeName

    def set_vehicleBias(self, vehicleBias):
        self.__vehicleBias = vehicleBias

    def set_routeLogic(self, routeLogic):
        self.__routeLogic = routeLogic


class StopIconFactory:
    def create_icon(self, vehicleObj: Vehicle):
        iconPath = vehicleObj.returnIconPath()
        return folium.CustomIcon(iconPath, icon_size=(40, 40))


class StopPopupFactory:
    @staticmethod
    def create_popup(stop_name):
        html = f'<div style="font-size: 16pt">{stop_name}</div>'
        iframe = IFrame(html, width=200, height=70)
        return folium.Popup(iframe, max_width=210, max_height=80)


class UI_Data:
    def __init__(self):
        self.__vehicles = {}  # Araçları tutan dictionary
        self.__routeList = []  # RouteObjleri tutuyor

    def get_vehicles(self):
        return self.__vehicles

    def get_routeList(self):
        return self.__routeList

    def set_vehicles(self, vehicles):
        self.__vehicles = vehicles

    def set_routeList(self, routeList):
        self.__routeList = routeList

    def add_vehicle(self, vehicle_type: str, vehicle: Vehicle):
       
        self.__vehicles[vehicle_type] = vehicle

    def add_route(self, route: RouteInfo):
        
        self.__routeList.append(route)

    def clear_routes(self):
        
        self.__routeList.clear()


class MapInitializer:
    def __init__(
        self,
        center_lat,
        center_lon,
        routePlannerObj: RoutePlanner,
        user: Passenger,
        ui_data: UI_Data,
        zoom_start=13.5,
    ):
        self.__map = folium.Map(
            location=[center_lat, center_lon], zoom_start=zoom_start
        )
        self.__transfer_line_group = folium.FeatureGroup(name="Aktarma Hatları").add_to(
            self.__map
        )
        self.__user_location = user.get_passengerLocation()
        self.__target_location = user.get_passengerTargetLocation()
        self.__routePlannerObj = routePlannerObj
        self.__ui_data = ui_data
        self.__user = user
        self.__taxi_line_group = ui_data.get_vehicles()["taxi"].returnMarkerGroup()
        self.__vehicles = ui_data.get_vehicles()
        self.__stops = routePlannerObj.stops
        self.__icon_factory = StopIconFactory()
        self.__popup_factory = StopPopupFactory()
        self.__just_taxi_route = folium.FeatureGroup(
            name="Sadece Taksi İle Yolculuk"
        ).add_to(self.__map)
        self.initialize_map()

    def get_map(self):
        return self.__map

    def get_transfer_line_group(self):
        return self.__transfer_line_group

    def get_user_location(self):
        return self.__user_location

    def get_target_location(self):
        return self.__target_location

    def get_routePlannerObj(self):
        return self.__routePlannerObj

    def get_ui_data(self):
        return self.__ui_data

    def get_user(self):
        return self.__user

    def get_taxi_line_group(self):
        return self.__taxi_line_group

    def get_vehicles(self):
        return self.__vehicles

    def get_stops(self):
        return self.__stops

    def get_icon_factory(self):
        return self.__icon_factory

    def get_popup_factory(self):
        return self.__popup_factory

    def get_just_taxi_route(self):
        return self.__just_taxi_route

    def set_map(self, map):
        self.__map = map

    def set_transfer_line_group(self, transfer_line_group):
        self.__transfer_line_group = transfer_line_group

    def set_user_location(self, user_location):
        self.__user_location = user_location

    def set_target_location(self, target_location):
        self.__target_location = target_location

    def set_routePlannerObj(self, routePlannerObj):
        self.__routePlannerObj = routePlannerObj

    def set_ui_data(self, ui_data):
        self.__ui_data = ui_data

    def set_user(self, user):
        self.__user = user

    def set_taxi_line_group(self, taxi_line_group):
        self.__taxi_line_group = taxi_line_group

    def set_vehicles(self, vehicles):
        self.__vehicles = vehicles

    def set_stops(self, stops):
        self.__stops = stops

    def set_icon_factory(self, icon_factory):
        self.__icon_factory = icon_factory

    def set_popup_factory(self, popup_factory):
        self.__popup_factory = popup_factory

    def set_just_taxi_route(self, just_taxi_route):
        self.__just_taxi_route = just_taxi_route

    def initialize_map(self):
        MousePosition().add_to(self.__map)

        for vehicle in self.__vehicles.values():
            vehicle.returnMarkerGroup().add_to(self.__map)

        for stop in self.__stops.values():
            self.add_stop_marker(stop, self.__icon_factory, self.__popup_factory)

        for stop_data in self.__stops.values():
            for next_stop in stop_data.get_nextStops():
                self.add_route_line(stop_data, next_stop)
            self.add_transfer_line(stop_data, stop_data.get_transfers())

        self.__user_marker_group = folium.FeatureGroup(
            name="Kullanıcı Lokasyonları"
        ).add_to(self.__map)
        folium.Marker(
            [self.__user_location.get_latitude(), self.__user_location.get_longitude()],
            popup="Başlangıç noktası",
            icon=folium.Icon(color="darkblue"),
        ).add_to(self.__user_marker_group)
        folium.Marker(
            [
                self.__target_location.get_latitude(),
                self.__target_location.get_longitude(),
            ],
            popup="Hedef noktası",
            icon=folium.Icon(color="red"),
        ).add_to(self.__user_marker_group)

        new_route_list = []
        for routeInfoObj in self.__ui_data.get_routeList():
            updated_route = self.__routePlannerObj.finalize_routes(
                self.__user,
                self.__user.get_passengerTargetLocation(),
                routeInfoObj.get_vehicleBias(),
                routeInfoObj.get_routeLogic(),
                routeInfoObj.get_routeName(),
            )
            new_route_list.append(updated_route)
        self.__ui_data.clear_routes()
        self.__ui_data.set_routeList(new_route_list)
        self.draw_taxi_line_if_needed(self.__ui_data.get_routeList()[0])
        self.draw_just_taxi_route()

    def add_stop_marker(self, stop, icon_factory, popup_factory):
        markerGroup = self.__vehicles[stop.get_type()].returnMarkerGroup()
        vehicleType = self.__vehicles[stop.get_type()]
        icon = icon_factory.create_icon(vehicleType)
        popup = popup_factory.create_popup(stop.get_name())

        folium.Marker(
            [stop.get_location().get_latitude(), stop.get_location().get_longitude()],
            icon=icon,
            popup=popup,
        ).add_to(markerGroup)

    def add_route_line(self, stop_data, next_stop):
        next_stop_id = next_stop["stopId"]
        next_stop_lat = self.__stops[next_stop_id].get_location().get_latitude()
        next_stop_lon = self.__stops[next_stop_id].get_location().get_longitude()

        line_color = self.__vehicles[stop_data.get_type()].linecolor
        marker_group = self.__vehicles[stop_data.get_type()].returnMarkerGroup()

        line_coordinates = [
            (
                stop_data.get_location().get_latitude(),
                stop_data.get_location().get_longitude(),
            ),
            (next_stop_lat, next_stop_lon),
        ]
        polyline = folium.PolyLine(
            line_coordinates, color=line_color, weight=6, opacity=1
        ).add_to(marker_group)
        PolyLineTextPath(
            polyline,
            "→",
            repeat=True,
            offset=17,
            attributes={"font-size": "72", "fill": line_color},
        ).add_to(marker_group)

    def add_transfer_line(self, stop_data, transfer):
        if transfer is not None:
            transfer_stop_id = transfer.get_transferStopId()
            transfer_stop_lat = (
                self.__stops[transfer_stop_id].get_location().get_latitude()
            )
            transfer_stop_lon = (
                self.__stops[transfer_stop_id].get_location().get_longitude()
            )

            line_coordinates = [
                (
                    stop_data.get_location().get_latitude(),
                    stop_data.get_location().get_longitude(),
                ),
                (transfer_stop_lat, transfer_stop_lon),
            ]
            folium.PolyLine(
                line_coordinates, color="purple", weight=6, opacity=1
            ).add_to(self.__transfer_line_group)

    def save_map(self, filename="map.html"):
        folium.LayerControl().add_to(self.__map)
        self.__map.save(filename)
        return os.path.abspath(filename)

    def draw_taxi_line_if_needed(self, routeInfoObj: RouteInfo):
        self.__taxi_line_group = folium.FeatureGroup(name="Taksi Yolu").add_to(
            self.__map
        )

        first_stop = routeInfoObj.get_route()[0]
        last_stop = routeInfoObj.get_route()[-1]

        distance_user_to_first_stop = DistanceCalculator.calculate_distance(
            self.__user_location.get_latitude(),
            self.__user_location.get_longitude(),
            first_stop.get_location().get_latitude(),
            first_stop.get_location().get_longitude(),
        )

        distance_target_to_last_stop = DistanceCalculator.calculate_distance(
            self.__target_location.get_latitude(),
            self.__target_location.get_longitude(),
            last_stop.get_location().get_latitude(),
            last_stop.get_location().get_longitude(),
        )
        distance_user_to_target = DistanceCalculator.calculate_distance(
            self.__user_location.get_latitude(),
            self.__user_location.get_longitude(),
            self.__target_location.get_latitude(),
            self.__target_location.get_longitude(),
        )
        distance_first_stop_to_target = DistanceCalculator.calculate_distance(
            first_stop.get_location().get_latitude(),
            first_stop.get_location().get_longitude(),
            self.__target_location.get_latitude(),
            self.__target_location.get_longitude(),
        )

        # Hedef nokta en yakın duraktan daha yakınsa, çizgi çizme
        if distance_user_to_target < distance_first_stop_to_target:
            return

        if distance_user_to_first_stop > 3:
            line_coordinates = [
                (
                    self.__user_location.get_latitude(),
                    self.__user_location.get_longitude(),
                ),
                (
                    first_stop.get_location().get_latitude(),
                    first_stop.get_location().get_longitude(),
                ),
            ]
            folium.PolyLine(
                line_coordinates, color="yellow", weight=8, opacity=1, dash_array="5, 5"
            ).add_to(self.__taxi_line_group)
        else:
            line_coordinates = [
                (
                    self.__user_location.get_latitude(),
                    self.__user_location.get_longitude(),
                ),
                (
                    first_stop.get_location().get_latitude(),
                    first_stop.get_location().get_longitude(),
                ),
            ]
            folium.PolyLine(
                line_coordinates, color="blue", weight=8, opacity=1, dash_array="5, 5"
            ).add_to(self.__user_marker_group)

        if distance_target_to_last_stop > 3:
            line_coordinates = [
                (
                    self.__target_location.get_latitude(),
                    self.__target_location.get_longitude(),
                ),
                (
                    last_stop.get_location().get_latitude(),
                    last_stop.get_location().get_longitude(),
                ),
            ]
            folium.PolyLine(
                line_coordinates, color="yellow", weight=8, opacity=1, dash_array="5, 5"
            ).add_to(self.__taxi_line_group)
        else:
            line_coordinates = [
                (
                    self.__target_location.get_latitude(),
                    self.__target_location.get_longitude(),
                ),
                (
                    last_stop.get_location().get_latitude(),
                    last_stop.get_location().get_longitude(),
                ),
            ]
            folium.PolyLine(
                line_coordinates, color="blue", weight=8, opacity=1, dash_array="5, 5"
            ).add_to(self.__user_marker_group)

    def draw_just_taxi_route(self):
        distance = DistanceCalculator.calculate_distance(
            self.__user_location.get_latitude(),
            self.__user_location.get_longitude(),
            self.__target_location.get_latitude(),
            self.__target_location.get_longitude(),
        )
        line_coordinates = [
            (self.__user_location.get_latitude(), self.__user_location.get_longitude()),
            (
                self.__target_location.get_latitude(),
                self.__target_location.get_longitude(),
            ),
        ]
        if distance > 3:
            lineColor = "orange"
            routeGroup = self.__taxi_line_group
        else:
            lineColor = "blue"
            routeGroup = self.__user_marker_group

        folium.PolyLine(
            line_coordinates, color=lineColor, weight=8, opacity=1, dash_array="5, 5"
        ).add_to(routeGroup)


class RoutePlannerWidget(QWidget):
    def __init__(self, user: Passenger, route_planner: RoutePlanner, ui_data: UI_Data):
        super().__init__()
        self.route_planner = route_planner
        self.user = user
        self.ui_data = ui_data
        self.init_ui()
        self.update_routes()

    def init_ui(self):
        main_layout = QVBoxLayout()

        self.routes_list = QListWidget()

        main_layout.addWidget(self.routes_list)

        self.setLayout(main_layout)
        self.setMaximumWidth(400)

    def update_routes(self):
        routes = self.ui_data.get_routeList()

        error_Text = ""

        credit_card_money_amount = self.user.get_creditCard_Money_Amount()
        cash_money_amount = self.user.get_cash_Money_Amount()
        kentkart_money_amount = self.user.get_kentCard_Money_Amount()

        self.routes_list.clear()

        if all(route.get_price() > routes[-1].get_price() for route in routes[:-1]) and routes[-1].get_price() > 0:
            if routes[-1].get_price() > cash_money_amount:
                error_Text = f"⚠️Hesabınızda yeterli nakit para yok!⚠️\n⚠️Alternatif bir rota seçiniz.⚠️\n"

            route_text = error_Text
            route_text += (
                f"{routes[-1].get_routeName()}: \nÜcret: {routes[-1].get_price():.2f} TL\n"
                f"Süre: {routes[-1].get_time():.2f} dakika\n"
                f"Mesafe: {routes[-1].get_distance():.2f} km\n\nDuraklar:\n"
            )
            self.routes_list.addItem(route_text)
            return

        for routeObjects in routes:
            if len(routeObjects.get_route()) > 0:
                distance_to_initial_stop = DistanceCalculator.calculate_distance(
                    self.user.get_passengerLocation().get_latitude(),
                    self.user.get_passengerLocation().get_longitude(),
                    routeObjects.get_route()[0].get_location().get_latitude(),
                    routeObjects.get_route()[0].get_location().get_longitude(),
                )
                distance_to_target_stop = DistanceCalculator.calculate_distance(
                    self.user.get_passengerTargetLocation().get_latitude(),
                    self.user.get_passengerTargetLocation().get_longitude(),
                    routeObjects.get_route()[-1].get_location().get_latitude(),
                    routeObjects.get_route()[-1].get_location().get_longitude(),
                )
                if (
                    routeObjects.get_price() > credit_card_money_amount
                    and routeObjects.get_price() > cash_money_amount
                    and routeObjects.get_price() > kentkart_money_amount
                ):
                    error_Text = f"⚠️Hesabınızda yeterli bakiye yok!⚠️\n⚠️Alternatif bir rota seçiniz.⚠️\n"
                if (
                    routeObjects.get_taxi_price() > cash_money_amount
                    and routeObjects.get_price() < credit_card_money_amount
                    and routeObjects.get_price() < kentkart_money_amount
                    and routeObjects.get_price() < cash_money_amount
                ):
                    error_Text = f"⚠️Taxi yolculuğu için yeterli nakitiniz yok!⚠️\n⚠️Alternatif bir rota seçiniz⚠️\n⚠️Ya da durağa yürüyerek gidiniz.⚠️\n"
            else:
                if routeObjects.get_price() > cash_money_amount:
                    error_Text = f"⚠️Hesabınızda yeterli nakit para yok!⚠️\n⚠️Alternatif bir rota seçiniz.⚠️\n"

            route_text = error_Text
            route_text += (
                f"{routeObjects.get_routeName()}: \nÜcret: {routeObjects.get_price():.2f} TL\n"
                f"Süre: {routeObjects.get_time():.2f} dakika\n"
                f"Mesafe: {routeObjects.get_distance():.2f} km\n\nDuraklar:\n"
            )

            if distance_to_initial_stop > 3 and len(routeObjects.get_route()) > 0:
                route_text += f"Taxi🚕-->{routeObjects.get_route()[0].get_name()}\n"
            elif distance_to_initial_stop < 3 and len(routeObjects.get_route()) > 0:
                route_text += f"Yürüyüş🚶-->{routeObjects.get_route()[0].get_name()}\n"

            route_text += "\n".join(
                [
                    f"{stops.get_name()} --> {next_stop.get_name()}"
                    + (
                        f" (Transfer🔁)"
                        if stops.get_transfers()
                        and stops.get_transfers().get_transferStopId()
                        == next_stop.get_stopid()
                        else ""
                    )
                    for stops, next_stop in zip(
                        routeObjects.get_route(), routeObjects.get_route()[1:]
                    )
                ]
            )
            if distance_to_target_stop > 3 and len(routeObjects.get_route()) > 0:
                route_text += f"\n{routeObjects.get_route()[-1].get_name()}-->Taxi🚕"
            elif distance_to_target_stop < 3 and len(routeObjects.get_route()) > 0:
                route_text += f"\n{routeObjects.get_route()[-1].get_name()}-->Yürüyüş🚶"

            self.routes_list.addItem(route_text)


class UserInfoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Kullanıcı Bilgileri")
        self.setMinimumWidth(400)

        # Ana layout
        main_layout = QVBoxLayout()

        # Yolcu tipi seçimi
        passenger_layout = QFormLayout()
        self.passenger_type_combo = QComboBox()
        self.passenger_type_combo.addItems(["Öğrenci", "Yaşlı", "Genel"])
        passenger_layout.addRow("Yolcu Tipi:", self.passenger_type_combo)
        main_layout.addLayout(passenger_layout)

        # Özel gün seçeneği
        self.special_day_checkbox = QCheckBox("Özel Gün Mü?")
        main_layout.addWidget(self.special_day_checkbox)

        # Kart listesi
        cards_label = QLabel("Kartlar:")
        main_layout.addWidget(cards_label)

        self.cards_list = QListWidget()
        main_layout.addWidget(self.cards_list)

        # Kart ekleme butonu
        add_card_button = QPushButton("Yeni Kart Ekle")
        add_card_button.clicked.connect(self.add_new_card)
        main_layout.addWidget(add_card_button)

        # Kart silme butonu
        remove_card_button = QPushButton("Seçili Kartı Sil")
        remove_card_button.clicked.connect(self.remove_selected_card)
        main_layout.addWidget(remove_card_button)

        # Butonlar
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

        self.setLayout(main_layout)

    def add_new_card(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Yeni Kart Ekle")
        layout = QFormLayout()

        # Kart tipi seçimi
        card_type_combo = QComboBox()
        card_type_combo.addItems(["Kredi Kartı", "Nakit", "KentKart"])
        layout.addRow("Kart Tipi:", card_type_combo)

        # Kart adı
        card_name = QLineEdit()
        layout.addRow("Kart Adı:", card_name)

        # Bakiye
        balance = QDoubleSpinBox()
        balance.setRange(0, 1000000)
        layout.addRow("Bakiye:", balance)

        # Butonlar
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)

        dialog.setLayout(layout)

        if dialog.exec_() == QDialog.Accepted:
            card_info = {
                "type": card_type_combo.currentText(),
                "name": card_name.text(),
                "balance": balance.value(),
            }
            self.cards_list.addItem(
                f"{card_info['type']} - {card_info['name']} ({card_info['balance']} TL)"
            )

    def remove_selected_card(self):
        current_item = self.cards_list.currentItem()
        if current_item:
            self.cards_list.takeItem(self.cards_list.row(current_item))

    def get_user_info(self):
        cards = []
        for i in range(self.cards_list.count()):
            card_text = self.cards_list.item(i).text()
            # Kart bilgilerini ayır
            parts = card_text.split(" - ")
            card_type = parts[0]
            # Kart adı ve bakiyeyi ayır
            name_balance = parts[1].split(" (")
            card_name = name_balance[0]
            # Bakiye kısmından tlyi ve parantezi kaldır
            balance = float(name_balance[1].replace(" TL)", ""))

            cards.append({"type": card_type, "name": card_name, "balance": balance})

        return {
            "passenger_type": self.passenger_type_combo.currentText(),
            "cards": cards,
            "special_day": self.special_day_checkbox.isChecked(),
        }

    def update_user_info(self, user_info):
        self.passenger_type_combo.setCurrentText(
            user_info.get("passenger_type", "Genel")
        )
        self.special_day_checkbox.setChecked(user_info.get("special_day", False))

        # Kartları temizle ve yeniden ekle
        self.cards_list.clear()
        for card in user_info.get("cards", []):
            self.cards_list.addItem(
                f"{card['type']} - {card['name']} ({card['balance']} TL)"
            )


class MainWindow(QMainWindow):
    def __init__(self, map_file_location, route_planner, user, ui_data):
        super().__init__()
        self.setWindowTitle("Rota Planlama Sistemi")
        self.setWindowIcon(QIcon(os.path.join(os.getcwd(), "appIcon.png")))
        self.route_planner = route_planner
        self.user = user
        self.ui_data = ui_data
        self.current_start_location = user.get_passengerLocation()
        self.current_target_location = user.get_passengerTargetLocation()

        # Ana layout
        main_layout = QHBoxLayout()

        # Rota planlayıcı widget'ı
        self.route_planner_widget = RoutePlannerWidget(
            user, route_planner, self.ui_data
        )
        main_layout.addWidget(self.route_planner_widget)

        # Web görünümü (harita)
        self.browser = QWebEngineView()
        self.browser.load(QUrl.fromLocalFile(map_file_location))
        main_layout.addWidget(self.browser)

        # Enlem ve boylam giriş alanları
        input_layout = QVBoxLayout()

        start_label = QLabel("Başlangıç (Enlem, Boylam):")
        input_layout.addWidget(start_label)
        self.start_lat_input = QLineEdit()
        self.start_lon_input = QLineEdit()
        input_layout.addWidget(self.start_lat_input)
        input_layout.addWidget(self.start_lon_input)

        target_label = QLabel("Hedef (Enlem, Boylam):")
        input_layout.addWidget(target_label)
        self.target_lat_input = QLineEdit()
        self.target_lon_input = QLineEdit()
        input_layout.addWidget(self.target_lat_input)
        input_layout.addWidget(self.target_lon_input)

        # Rotayı güncelle butonu
        self.update_route_button = QPushButton("Rotayı Güncelle")
        self.update_route_button.clicked.connect(self.update_route)
        input_layout.addWidget(self.update_route_button)

        # Kullanıcı bilgileri butonu
        self.user_info_button = QPushButton("Kullanıcı Bilgileri")
        self.user_info_button.clicked.connect(self.show_user_info_dialog)
        input_layout.addWidget(self.user_info_button)

        # Etiketler
        self.passenger_type_label = QLabel(f"Yolcu Tipi: {user.get_passenger_type()}")
        self.payment_type_label = QLabel("Ödeme Tipi: Yok")
        self.balance_label = QLabel("Bakiye: Yok")
        self.balance_labet = QLabel("Özel Gün Mü ?")

        # Etiketleri layout'a ekle
        input_layout.addWidget(self.passenger_type_label)
        input_layout.addWidget(self.payment_type_label)
        input_layout.addWidget(self.balance_label)

        # Giriş alanlarını içeren widget ve layout'u ana layout'a ekleme
        input_widget = QWidget()
        input_widget.setLayout(input_layout)
        input_widget.setMaximumWidth(200)
        main_layout.addWidget(input_widget)

        # Merkezi widget ve layout ayarı
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.update_ui()

    def update_ui(self):

        self.passenger_type_label.setText(
            f"Yolcu Tipi: {self.user.get_passenger_type()}"
        )

        payment_info = "Ödeme Tipi:\n"
        credit_balance = 0.0
        cash_balance = 0.0
        kent_balance = 0.0

        if self.user.get_creditCards():
            credit_balance = sum(card.balance for card in self.user.get_creditCards())
            payment_info += f"Kredi Kartı: {credit_balance:.2f} TL\n"
        else:
            payment_info += "Kredi Kartı: 0.00 TL\n"

        if self.user.get_cash_cards():
            cash_balance = sum(card.balance for card in self.user.get_cash_cards())
            payment_info += f"Nakit: {cash_balance:.2f} TL\n"
        else:
            payment_info += "Nakit: 0.00 TL\n"

        if self.user.get_kent_cards():
            kent_balance = sum(card.balance for card in self.user.get_kent_cards())
            payment_info += f"KentKart: {kent_balance:.2f} TL\n"
        else:
            payment_info += "KentKart: 0.00 TL\n"

        self.payment_type_label.setText(payment_info)
        self.balance_label.setText(
            f"Toplam Bakiye: {credit_balance + cash_balance + kent_balance:.2f} TL"
        )

        self.route_planner_widget.update_routes()

    def update_route(self):
        new_start_location = None
        new_target_location = None
        try:
            start_lat = float(self.start_lat_input.text())
            start_lon = float(self.start_lon_input.text())
            target_lat = float(self.target_lat_input.text())
            target_lon = float(self.target_lon_input.text())

            new_start_location = Location(start_lat, start_lon)
            new_target_location = Location(target_lat, target_lon)

            self.current_start_location = new_start_location
            self.current_target_location = new_target_location

            self.update_map_and_route(new_start_location, new_target_location)
        except ValueError:
            print("Geçersiz enlem veya boylam girişi.")

    def update_map_and_route(self, start_location, target_location):
        self.user.set_passengerLocation(start_location)
        self.user.set_passengerTargetLocation(target_location)
        map_initializer = MapInitializer(
            40.7933, 29.9515, self.route_planner, self.user, self.ui_data
        )
        map_file = map_initializer.save_map()
        self.browser.load(QUrl.fromLocalFile(map_file))
        self.route_planner_widget.update_routes()

    def show_user_info_dialog(self):
        dialog = UserInfoDialog(self)

        current_user_info = {
            "passenger_type": self.user.get_passenger_type(),
            "special_day": self.user.get_is_special_day(),
            "cards": [],
        }

        for card in self.user.get_creditCards():
            current_user_info["cards"].append(
                {"type": "Kredi Kartı", "name": "Kredi Kartı", "balance": card.balance}
            )
        for card in self.user.get_cash_cards():
            current_user_info["cards"].append(
                {"type": "Nakit", "name": "Nakit", "balance": card.balance}
            )
        for card in self.user.get_kent_cards():
            current_user_info["cards"].append(
                {"type": "KentKart", "name": "KentKart", "balance": card.balance}
            )

        dialog.update_user_info(current_user_info)

        if dialog.exec_() == QDialog.Accepted:
            user_info = dialog.get_user_info()
            self.update_user_info(user_info)

    def update_user_info(self, user_info):
        passenger_type = user_info["passenger_type"]
        cards = user_info["cards"]
        special_day = user_info["special_day"]

        current_location = self.user.get_passengerLocation()
        current_target = self.user.get_passengerTargetLocation()

        credit_cards = []
        cash_cards = []
        kent_cards = []

        for card in cards:
            payment_object = None
            if card["type"] == "Kredi Kartı":
                payment_object = KrediKarti(card["balance"])
                credit_cards.append(payment_object)
            elif card["type"] == "Nakit":
                payment_object = Nakit(card["balance"])
                cash_cards.append(payment_object)
            elif card["type"] == "KentKart":
                payment_object = KentKart(card["balance"])
                kent_cards.append(payment_object)

        if passenger_type == "Öğrenci":
            new_user = Student(
                passenger_type,
                current_location,
                current_target,
                credit_cards,
                cash_cards,
                kent_cards,
                special_day,
            )
        elif passenger_type == "Yaşlı":
            new_user = Elderly(
                passenger_type,
                current_location,
                current_target,
                credit_cards,
                cash_cards,
                kent_cards,
                special_day,
            )
        else:
            new_user = General(
                passenger_type,
                current_location,
                current_target,
                credit_cards,
                cash_cards,
                kent_cards,
                special_day,
            )

        self.user = new_user
        self.route_planner_widget.user = new_user

        self.update_map_and_route(current_location, current_target)
        self.update_ui()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    stops = StopLoader.load_stops_from_json("veriseti.json")
    distance_calculator = DistanceCalculator()

    taxi_feature_group = folium.FeatureGroup(name="Taksi Yolu")
    taxi = Taxi(0, 0, taxi_feature_group)
    taxi.set_fees("veriseti.json")

    vehicles = {
        "bus": Bus("busIcon.png", folium.FeatureGroup(name="Otobüs Durakları")),
        "tram": Tram("tramIcon.png", folium.FeatureGroup(name="Tramvay Durakları")),
        "taxi": taxi,
    }
    route_planner = RoutePlanner(stops, vehicles, distance_calculator)
    standard_route_logic = bellmanFord_Standard()
    least_stops_route_logic = bellmanFord_LeastStops()
    taxi_route_logic = TaxiRouteLogic(taxi)

    user_location = Location(40.80056, 29.97302)
    target_location = Location(40.77736, 29.8956)
    user = General("Genel", user_location, target_location, None, None, None)

    ui_data = UI_Data()
    ui_data.set_vehicles(vehicles)

    # rotalar
    mostOptimizedRoute = route_planner.finalize_routes(
        user,
        user.get_passengerTargetLocation(),
        "None",
        standard_route_logic,
        "🏁En Optimal Rota🏁",
    )
    ui_data.add_route(mostOptimizedRoute)
    busBasedRoute = route_planner.finalize_routes(
        user,
        user.get_passengerTargetLocation(),
        "bus",
        standard_route_logic,
        "🚌Otobüs ağırlıklı rota🚌",
    )
    ui_data.add_route(busBasedRoute)
    tramBasedRoute = route_planner.finalize_routes(
        user,
        user.get_passengerTargetLocation(),
        "tram",
        standard_route_logic,
        "🚋Tramvay ağırlıklı rota🚋",
    )
    ui_data.add_route(tramBasedRoute)
    leastStopsRoute = route_planner.finalize_routes(
        user,
        user.get_passengerTargetLocation(),
        "None",
        least_stops_route_logic,
        "🛑En az aktarmalı rota🛑",
    )
    ui_data.add_route(leastStopsRoute)
    justtaxiRoute = route_planner.finalize_routes(
        user,
        user.get_passengerTargetLocation(),
        "taxi",
        taxi_route_logic,
        "🚕Sadece Taksi Kullanarak Yolculuk🚕",
    )
    ui_data.add_route(justtaxiRoute)

    map_initializer = MapInitializer(40.7933, 29.9515, route_planner, user, ui_data)
    map_file = map_initializer.save_map()
    window = MainWindow(map_file, route_planner, user, ui_data)
    window.show()
    sys.exit(app.exec_())
