from typing import Any, Optional, Set, Dict
from enum import Enum
import datetime
import abc
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
    def __init__(self, name: str, spot_type: SpotTypeEnum, is_vip: bool = False, is_reserved: bool = False) -> None:
        self.name = name
        self.spot_type = spot_type
        self.vehicle = None
        self.is_vip = is_vip
        self.is_reserved = is_reserved


class ParkingHistory:
    def __init__(
        self,
        vehicle: Vehicle,
        spot: Spot,
        from_time: Optional[datetime.datetime] = None,
        to_time: Optional[datetime.datetime] = None
    ):
        self.vehicle = vehicle
        self.spot = spot
        self.from_time = from_time
        self.to_time = to_time


class Row:
    def __init__(self, name: str, spots: Set[Spot]) -> None:
        self.name = name
        self.spots = spots

    @property
    def number_of_spots(self) -> int:
        return len(self.spots)


class Level:
    def __init__(self, name: str, rows: Set[Row]) -> None:
        self.name = name
        self.rows = rows
        self.number_of_spots = 0

        for row in rows:
            self.number_of_spots += row.number_of_spots

    @property
    def number_of_rows(self) -> int:
        return len(self.rows)


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


class SpotFee(abc.ABC):
    @abc.abstractmethod
    def __init__(self) -> None:
        ...

    @abc.abstractmethod
    def calculate_fee(self) -> None:
        ...


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

    def calculcate_fee(
        self,
        spot: Spot
    ) -> float:
        ...


class Ticket:
    def __init__(self, vehicle: Vehicle) -> None:
        self.vehicle = vehicle
        self.parking_history = None


class TicketManager:
    def create_ticket(self, vehicle) -> Ticket:
        return Ticket(vehicle=vehicle)


class AvailableSpots:
    def __init__(self) -> None:
        self.available_spots = defaultdict(set)

    def __getitem__(self, key: str) -> Set[Spot]:
        return self.available_spots[key]

    def __setitem__(self, key: str, value: Set[Spot]) -> None:
        self.available_spots[key] = value


class ParkingHistoryStore:
    def __init__(self) -> None:
        self.parking_history: Set[ParkingHistory] = set()


class AvailableSpotsObserver:
    def __init__(self, available_spots: AvailableSpots) -> None:
        self.available_spots = available_spots


class ParkingHistoryObserver:
    def __init__(self, parking_history: ParkingHistoryStore) -> None:
        self.parking_history = parking_history


class EntryGate:
    def __init__(
        self,
        ticket_manager: TicketManager,
        available_spot_observer: AvailableSpotsObserver,
        parking_history_observer: ParkingHistoryObserver
    ) -> None:
        self.available_spot_observer = available_spot_observer
        self.ticket_manager = ticket_manager
        self.parking_history_observer = parking_history_observer


class ExitGate:
    def __init__(
        self,
        ticket_manager: TicketManager,
        available_spot_observer: AvailableSpotsObserver,
        parking_history_observer: ParkingHistoryObserver
    ) -> None:
        self.available_spot_observer = available_spot_observer
        self.ticket_manager = ticket_manager
        self.parking_history_observer = parking_history_observer


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
            self.available_spots[spot_location.spot.spot_type].add(
                spot_location)
            if self.fee_structure[spot_location.spot.spot_type] is None:
                # @TODO Change later with well defined exception.
                raise Exception
            self.levels.add(spot_location.level)

        for level in self.levels:
            self.number_of_levels += 1
            self.number_of_rows += level.number_of_rows
            self.number_of_spots += level.number_of_spots
