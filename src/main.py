from typing import Optional, Set
from enum import Enum
import datetime
from collections import defaultdict


class SpotTypeEnum(str, Enum):
    cycle = "cycle"
    motor_cycle = "motor_cycle"
    compact_vehicle = "compact_car"
    regular_vehicle = "regular_car"
    handicapped_spot = "handicapped_spot"
    electric_vehicle = "electric_vehicle"


class Vehicle:
    def __init__(self, licence_plate: str, vehicle_type: SpotTypeEnum) -> None:
        self.licence_plate = licence_plate
        self.vehicle_type = vehicle_type


class Spot:
    def __init__(
        self,
        name: str,
        spot_type: SpotTypeEnum
    ) -> None:
        self._name = name
        self._spot_type = spot_type
        self._vehicle = None
        self._has_been_booked = False

    @property
    def spot_type(self) -> SpotTypeEnum:
        return self._spot_type
    
    @property
    def name(self) -> str:
        return self.name
    
    @property
    def is_available(self) -> bool:
        return self._vehicle is None and not self._has_been_booked
    
    def book(self) -> None:
        self._has_been_booked = True
    
    def park_vehicle(self, vehicle: Vehicle) -> None:
        self._vehicle = vehicle

    def remove_vehicle(self, vehicle: Vehicle) -> None:
        self._vehicle = None
        self._has_been_booked = False


class ParkingHistory:
    def __init__(
        self,
        vehicle: Vehicle,
        spot: Spot
    ):
        self._vehicle = vehicle
        self._spot = spot
        self._from_time = datetime.datetime.now()
        self._to_time = None
        self._spot.park_vehicle(self._vehicle)

    def exit(self) -> None:
        self._to_time = datetime.datetime.now()
        self._spot.remove_vehicle(self._vehicle)

    def get_total_parking_time(self) -> int:
        '''
        Returns number of seconds the vehicle was standing here.
        If vehicle is still parked, it will raise an exception.
        '''
        if self._from_time is not None and self._to_time is not None:
            return (self._to_time - self._from_time).seconds
        raise Exception #@TODO better handling required


class Row:
    def __init__(self, name: str, spots: Set[Spot]) -> None:
        self._name = name
        self._spots = spots

    @property
    def number_of_spots(self) -> int:
        return len(self._spots)
    
    @property
    def name(self) -> str:
        return self._name


class Level:
    def __init__(self, name: str, rows: Set[Row]) -> None:
        self._name = name
        self._rows = rows
        self.number_of_spots = 0

        for row in self._rows:
            self.number_of_spots += row.number_of_spots

    @property
    def number_of_rows(self) -> int:
        return len(self._rows)
    
    @property
    def name(self) -> str:
        return self._name


class SpotHierarchy:
    def __init__(
        self,
        level: Level,
        row: Row,
        spot: Spot
    ) -> None:
        self.level = level
        self.row = row
        self.spot = spot


class AvailableSpots:
    def __init__(self) -> None:
        self.available_spots = defaultdict(set)

    def add_to_available_spots(self, spot: Spot) -> None:
        self.available_spots[spot.spot_type].add(spot)

    def remove_from_available_spots(self, spot: Spot) -> None:
        self.available_spots[spot.spot_type].remove(spot)


class ParkingHistoryStore:
    def __init__(self) -> None:
        self.parking_history_store: Set[ParkingHistory] = set()

    def add(self, parking_history: ParkingHistory) -> None:
        self.parking_history_store.add(parking_history)


class AvailableSpotsObserver:
    def __init__(self, available_spots: AvailableSpots) -> None:
        self.available_spots = available_spots

    def add_to_available_spots(self, spot: Spot) -> None:
        self.available_spots.add_to_available_spots(spot)
    
    def remove_from_available_spots(self, spot: Spot) -> None:
        self.available_spots.remove_from_available_spots(spot)

    def notify_park(self, spot: Spot) -> None:
        self.remove_from_available_spots(spot)

    def notify_exit(self, spot: Spot) -> None:
        self.add_to_available_spots(spot)


class ParkingHistoryObserver:
    def __init__(self, parking_history_store: ParkingHistoryStore) -> None:
        self.parking_history_store = parking_history_store

    def add_to_parking_history(self, parking_history: ParkingHistory) -> None:
        self.parking_history_store.add(parking_history)

    def notify(self, parking_history: ParkingHistory) -> None:
        self.add_to_parking_history(parking_history)



class Ticket:
    def __init__(
        self,
        vehicle: Vehicle,
        spot: Spot
    ) -> None:
        self._vehicle = vehicle
        self._spot = spot
        self._parking_history = None
        self._parked_at: Optional[datetime.datetime] = None
        self._exit_at: Optional[datetime.datetime] = None

    @property
    def spot(self) -> Spot:
        return self.spot

    @property
    def parking_history(self) -> ParkingHistory:
        return self._parking_history

    def calculate_total_parking_time(self) -> int:
        '''
        Returns number of seconds the vehicle was standing here.
        If vehicle is still parked, it will raise an exception.
        '''
        if self._parked_at is not None and self._exit_at is not None:
            return (self._parked_at - self._exit_at).seconds
        raise Exception #@TODO better handling required
    
    def park(self) -> None:
        self._parked_at = datetime.datetime.now()
        self._parking_history = ParkingHistory(self._vehicle, self._spot)

    def exit(self) -> None:
        self._exit_at = datetime.datetime.now()
        self._parking_history.exit()


class TicketManager:
    def __init__(
        self, 
        available_spot_observer: AvailableSpotsObserver,
        parking_history_observer: ParkingHistoryObserver
    ):
        self.available_spot_observer = available_spot_observer
        self.parking_history_observer = parking_history_observer

    def _notify_parking_history_observer(self, ticket: Ticket) -> None:
        self.parking_history_observer.notify(ticket.parking_history)

    def _notify_entry_available_spot_observer(self, ticket: Ticket) -> None:
        self.available_spot_observer.notify_park(ticket.spot)

    def _notify_exit_available_spot_observer(self, ticket: Ticket) -> None:
        self.available_spot_observer.notify_exit(ticket.spot)

    def _entry_notify(self, ticket: Ticket) -> None:
        self._notify_entry_available_spot_observer(ticket)
        self._notify_parking_history_observer(ticket)

    def _exit_notify(self, ticket: Ticket) -> None:
        self._notify_exit_available_spot_observer(ticket)

    def create_ticket(self, vehicle: Vehicle, spot: Spot) -> Ticket:
        if vehicle.vehicle_type != spot.spot_type or not spot.is_available:
            raise Exception #@TODO Better exceptional handling needed.
        spot.book(vehicle)
        return Ticket(vehicle=vehicle, spot=spot)
    
    def park(self, ticket: Ticket) -> None:
        ticket.park()
        self._entry_notify(ticket)

    def exit(self, ticket: Ticket) -> None:
        ticket.exit()
        self._exit_notify(ticket)
        


class SpotFee:
    def __init__(
        self,
        base_fee: float,
        fee_per_minute: float
    ):
        self.base_fee = base_fee
        self.fee_per_minute = fee_per_minute

    def calculate_fee(self, ticket: Ticket) -> float:
        return round(ticket.calculate_total_parking_time()*self.fee_per_minute/60 + self.base_fee, 2)


class CycleFee(SpotFee):
    ...


class MotorCycleFee(SpotFee):
    ...


class CompactVehicleFee(SpotFee):
    ...


class RegularVehicleFee(SpotFee):
    ...


class HandicappedSpotFee(SpotFee):
    ...


class ElectricVehicleFee(SpotFee):
    ...


class FeeStructure:
    def __init__(
        self,
        cycle_fee: Optional[CycleFee] = None,
        motorcyclefee: Optional[MotorCycleFee] = None,
        compactvehiclefee: Optional[CompactVehicleFee] = None,
        regularvehiclefee: Optional[RegularVehicleFee] = None,
        handicappedspotfee: Optional[HandicappedSpotFee] = None,
        electricvehiclefee: Optional[ElectricVehicleFee] = None
    ):
        self.fee_structure = {
            SpotTypeEnum.cycle: cycle_fee,
            SpotTypeEnum.motor_cycle: motorcyclefee,
            SpotTypeEnum.compact_vehicle: compactvehiclefee,
            SpotTypeEnum.regular_vehicle: regularvehiclefee,
            SpotTypeEnum.electric_vehicle: electricvehiclefee,
            SpotTypeEnum.handicapped_spot: handicappedspotfee
        }


class EntryGate:
    def __init__(
        self,
        ticket_manager: TicketManager,
    ) -> None:
        self.ticket_manager = ticket_manager


class ExitGate:
    def __init__(
        self,
        ticket_manager: TicketManager
    ) -> None:
        self.ticket_manager = ticket_manager


class EntryGateManager:
    def __init__(self, gates: Set[EntryGate]) -> None:
        self.gates = gates


class ExitGateManager:
    def __init__(self, gates: Set[ExitGate]) -> None:
        self.gates = gates


class ParkingLot:
    def __init__(
        self,
        name: str,
        spot_locations: Set[SpotHierarchy],
        fee_structure: FeeStructure,
        entry_gate_manager: EntryGateManager,
        exit_gate_manager: ExitGateManager,
        available_spots: AvailableSpots,
        parking_history: ParkingHistoryStore,
        location: Optional[str] = None
    ) -> None:
        self.name = name
        self.location = location
        self.spot_locations = spot_locations
        self.number_of_levels = 0
        self.number_of_rows = 0
        self.number_of_spots = 0
        self.available_spots = available_spots
        self.fee_structure = fee_structure
        self.levels: Set[Level] = set()
        self.parking_history = parking_history
        self.entry_gate_manager = entry_gate_manager
        self.exit_gate_manager = exit_gate_manager

        for spot_location in spot_locations:
            self.available_spots.available_spots[spot_location.spot.spot_type].add(
                spot_location)
            if self.fee_structure[spot_location.spot.spot_type] is None:
                # @TODO Change later with well defined exception.
                raise Exception
            self.levels.add(spot_location.level)

        for level in self.levels:
            self.number_of_levels += 1
            self.number_of_rows += level.number_of_rows
            self.number_of_spots += level.number_of_spots
