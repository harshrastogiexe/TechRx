# Built-in imports
import ast, re, os
from logging import getLogger
# Third-party imports
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction
# Rule-based imports
from scripts.logics import Logics
from medicines.extract_text import MedicineListExtractor
from med_price_compare.compare_prices import ComparePrices
from typing import Any, Dict, List, Text

logger = getLogger(__name__)
class ValidateMedicalForm(FormAction):
	def name(self) -> Text:
		"""
		Method for name

		:return: Text
		"""
		return "validate_medical_form"

	@staticmethod
	def required_slots(tracker: Tracker) -> List[Text]:
		"""
		Method for required_slots

		:param tracker: Tracker
		:return: List[Text]
		"""
		return ["symptom", "age", "gender", "location"]

	def slot_mappings(self) -> Dict[Text, Any]:
		"""
		Method for slot_mappings

		:return: Dict[Text, Any]
		"""
		return {
			"symptom": self.from_text(),
			"age": self.from_text(),
			"gender": self.from_text(),
			"location": self.from_text(),
		}

	def validate_symptom(
		self,
		value: Any,
		dispatcher: CollectingDispatcher,
		tracker: Tracker,
		domain: Dict[Text, Any],
	) -> Dict[Text, Any]:
		"""
		Method for validate_symptom

		:param value: Any
		:param dispatcher: CollectingDispatcher
		:param tracker: Tracker
		:param domain: Dict[Text, Any]
		:return: Dict[Text, Any]
		"""
		# Perform your slot validation logic here
		# Return a dictionary with a 'isValid' key and a boolean value

		words = Logics.get_words(value)
		symptoms = Logics.get_symptoms(words=words)
		if symptoms:
			return {"symptom": str(symptoms)}
		else:
			dispatcher.utter_template(template="utter_ask_symptom", tracker=tracker)
			return {"symptom": None}

	def validate_age(
		self,
		value: Any,
		dispatcher: CollectingDispatcher,
		tracker: Tracker,
		domain: Dict[Text, Any],
	) -> Dict[Text, Any]:
		"""
		Method for validate_age

		:param  value: Any
		:param  dispatcher: CollectingDispatcher
		:param  tracker: Tracker
		:param  domain: Dict[Text, Any]
		:return: Dict[Text, Any]
		"""
		# Perform your slot validation logic here
		# Return a dictionary with a 'isValid' key and a boolean value

		min_age = 0
		max_age = 100

		if isinstance(value, str) and value.isdigit():
			age = int(value)
			if min_age <= age <= max_age:
				return {"age": value}
		dispatcher.utter_template(template="utter_ask_age", tracker=tracker)
		return {"age": None}

	def validate_gender(
		self,
		value: Any,
		dispatcher: CollectingDispatcher,
		tracker: Tracker,
		domain: Dict[Text, Any],
	) -> Dict[Text, Any]:
		"""
		Method for validate_gender

		:param value: Any
		:param dispatcher: CollectingDispatcher
		:param tracker: Tracker
		:param domain: Dict[Text, Any]
		:return:
		"""
		# Perform your slot validation logic here
		# Return a dictionary with a 'isValid' key and a boolean value

		valid_genders = ["male", "female", "other"]

		if isinstance(value, str) and value.lower() in valid_genders:
			return {"gender": value}
		else:
			dispatcher.utter_template(template="utter_ask_gender", tracker=tracker)
			return {"gender": None}

	def validate_location(
		self,
		value: Any,
		dispatcher: CollectingDispatcher,
		tracker: Tracker,
		domain: Dict[Text, Any],
	) -> Dict[Text, Any]:
		"""
		Method for validate_location

		:param value: Any,
		:param dispatcher: CollectingDispatcher,
		:param tracker: Tracker,
		:param domain: Dict[Text, Any],
		:return:
		"""
		# Perform your slot validation logic here
		# Return a dictionary with a 'isValid' key and a boolean value

		if isinstance(value, str):
			return {"location": value}
		else:
			dispatcher.utter_template(template="utter_ask_location", tracker=tracker)
			return {"location": None}

	def submit(
		self,
		dispatcher: CollectingDispatcher,
		tracker: Tracker,
		domain: Dict[Text, Any],
	) -> List[Dict]:
		"""
		Method for submit

		:param dispatcher: CollectingDispatcher,
		:param tracker: Tracker,
		:param domain: Dict[Text, Any],
		:return:
		"""
		symptom = ast.literal_eval(tracker.get_slot("symptom")) or []
		age = tracker.get_slot("age")
		gender = tracker.get_slot("gender")
		location = tracker.get_slot("location")

		message = f"""
            symptom: {symptom}
            age: {age}
            gender: {gender}
            location: {location}
        """
		diseases = Logics.get_disease_by_symptoms(symptoms=symptom)
		if diseases:
			message += f"\nI found the following health issue that match your symptoms:"
			for i, d in enumerate(diseases):
				message += f"\n {i}: {d}"
		else:
			message += (
				"\nI'm sorry, I couldn't find any health issue that match your symptoms."
			)
		dispatcher.utter_message(message)

		# Set all slots to None
		slots = []
		for slot_name in tracker.slots.keys():
			slots.append(SlotSet(slot_name, None))

		return slots


class ActionFallback(Action):
	"""
	Method for ActionFallback

	:param Action:
	:return:
	"""

	def name(self) -> Text:
		"""
		Method for name

		:return: Text
		"""
		return "action_fallback"

	def run(
		self,
		dispatcher: CollectingDispatcher,
		tracker: Tracker,
		domain: Dict[Text, Any],
	) -> List[Dict[Text, Any]]:
		"""
		Method for run

		:param dispatcher: CollectingDispatcher,
		:param tracker: Tracker,
		:param domain: Dict[Text, Any],

		:return: List[Dict[Text, Any]]
		"""

		# get Tracker State
		# extract user_message from latest_message
		state = tracker.current_state()
		user_message = state["latest_message"]["text"]

		response = Logics.get_fallback_response(user_message=user_message)
		dispatcher.utter_message(text=response)
		return []


class ValidateDoctorForm(FormAction):
	"""
	Method for ActionFindDoctor

	:param Action:
	:return:
	"""

	def name(self) -> Text:
		"""
		Method for name

		:return: Text
		"""
		return "validate_doctor_form"

	@staticmethod
	def required_slots(tracker: Tracker) -> List[Text]:
		"""
		Method for required_slots

		:param tracker: Tracker
		:return: List[Text]
		"""
		return ["disease"]

	def slot_mappings(self) -> Dict[Text, Any]:
		"""
		Method for slot_mappings

		:return: Dict[Text, Any]
		"""
		return {
			"disease": self.from_text()
		}

	def validate_disease(
		self,
		value: Any,
		dispatcher: CollectingDispatcher,
		tracker: Tracker,
		domain: Dict[Text, Any],
	) -> Dict[Text, Any]:
		"""
		Method for validate_disease

		:param value: Any
		:param dispatcher: CollectingDispatcher
		:param tracker: Tracker
		:param domain: Dict[Text, Any]
		:return: Dict[Text, Any]
		"""
		# Perform your slot validation logic here
		# Return a dictionary with a 'isValid' key and a boolean value

		words = Logics.get_words(value)
		doctors = Logics.get_doctors(diseases=words)
		if doctors:
			return {"doctors": f"'str(doctors)'"}
		else:
			dispatcher.utter_template(template="utter_ask_disease", tracker=tracker)
		return {"doctors": None}

	def submit(
		self,
		dispatcher: CollectingDispatcher,
		tracker: Tracker,
		domain: Dict[Text, Any]
	) -> List[Dict[Text, Any]]:
		"""
		Method for run

		:param dispatcher: CollectingDispatcher,
		:param tracker: Tracker,
		:param domain: Dict[Text, Any],

		:return: List[Dict[Text, Any]]
		"""
		state = tracker.current_state()
		user_message = state["latest_message"]["text"]

		message = ""
		doctors = Logics.get_doctors(user_message)
		if doctors:
			message += f"\nI found the following doctors that match your disease:"
			for i, d in enumerate(doctors):
				message += f"\n {i+1}: {d}"
		else:
			message += (
				"\nI'm sorry, I couldn't find any doctors that match your disease."
			)

		dispatcher.utter_message(message)

		# Set all slots to None
		slots = []
		for slot_name in tracker.slots.keys():
			slots.append(SlotSet(slot_name, None))

		return slots


class ValidateMedicineForm(FormAction):
	"""
	Method for ActionFindMedicine

	:param Action:
	:return:
	"""

	def name(self) -> Text:
		"""
		Method for name

		:return: Text
		"""
		return "validate_medicine_form"

	@staticmethod
	def required_slots(tracker: Tracker) -> List[Text]:
		"""
		Method for required_slots

		:param tracker: Tracker
		:return: List[Text]
		"""
		return ["prescription"]

	def slot_mappings(self) -> Dict[Text, Any]:
		"""
		Method for slot_mappings

		:return: Dict[Text, Any]
		"""
		return {
			"prescription": self.from_text()
		}

	def validate_prescription(
		self,
		value: Any,
		dispatcher: CollectingDispatcher,
		tracker: Tracker,
		domain: Dict[Text, Any],
	) -> Dict[Text, Any]:
		"""
		Method for validate_prescription

		:param value: Any
		:param dispatcher: CollectingDispatcher
		:param tracker: Tracker
		:param domain: Dict[Text, Any]
		:return: Dict[Text, Any]
		"""
		# Perform your slot validation logic here
		# Return a dictionary with a 'isValid' key and a boolean value
		state = tracker.current_state()
		prescription_filename = state["latest_message"]["text"] or []
		message = ''
		medicine_names = MedicineListExtractor.final_text(prescription_filename)
		if medicine_names:
			message += 'File found! extracting medicine names'
			dispatcher.utter_message(message)
			return medicine_names
		else:
			message += 'File not found please recheck the filename'
			dispatcher.utter_message(message)
			return {"medicine_names": None}

	def submit(
		self,
		dispatcher: CollectingDispatcher,
		tracker: Tracker,
		domain: Dict[Text, Any]
	) -> List[Dict[Text, Any]]:
		"""
		Method for run

		:param dispatcher: CollectingDispatcher,
		:param tracker: Tracker,
		:param domain: Dict[Text, Any],

		:return: List[Dict[Text, Any]]
		"""
		state = tracker.current_state()
		prescription_filename = state["latest_message"]["text"]

		medicine_names = MedicineListExtractor.final_text(prescription_filename)

		message = ''

		if medicine_names:
			message += f"\nI found the following following medicines in your prescription"

			for i, d in enumerate(medicine_names):
				message += f"\n {i+1}: {d}"
		else:
			message += (
				"\nI'm sorry, I couldn't find any medicines in your prescription. Please enter manually."
			)

		dispatcher.utter_message(message)
		# Set all slots to None
		slots = []
		for slot_name in tracker.slots.keys():
			slots.append(SlotSet(slot_name, None))

		return slots

	class ValidatePriceForm(FormAction):
		"""
		Method for ActionMedicinePrice

		:param Action:
		:return:
		"""

		def name(self) -> Text:
			"""
			Method for name

			:return: Text
			"""
			return "validate_price_form"

		@staticmethod
		def required_slots(tracker: Tracker) -> List[Text]:
			"""
			Method for required_slots

			:param tracker: Tracker
			:return: List[Text]
			"""
			return ["medicine_name"]

		def slot_mappings(self) -> Dict[Text, Any]:
			"""
			Method for slot_mappings

			:return: Dict[Text, Any]
			"""
			return {
				"medicine_name": self.from_text()
			}

		def validate_medicine_name(
			self,
			value: Any,
			dispatcher: CollectingDispatcher,
			tracker: Tracker,
			domain: Dict[Text, Any],
		) -> Dict[Text, Any]:
			"""
			Method for validate_medicine_name

			:param value: Any
			:param dispatcher: CollectingDispatcher
			:param tracker: Tracker
			:param domain: Dict[Text, Any]
			:return: Dict[Text, Any]
			"""
			# Perform your slot validation logic here
			# Return a dictionary with a 'isValid' key and a boolean value
			state = tracker.current_state()
			medicine_name = re.sub(r"[.,-]", "", state["latest_message"]["text"]) or []

			return {"medicine_name": medicine_name}
		def submit(
			self,
			dispatcher: CollectingDispatcher,
			tracker: Tracker,
			domain: Dict[Text, Any]
		) -> List[Dict[Text, Any]]:
			"""
			Method for run

			:param dispatcher: CollectingDispatcher,
			:param tracker: Tracker,
			:param domain: Dict[Text, Any],

			:return: List[Dict[Text, Any]]
			"""
			state = tracker.current_state()
			medicine_name =  re.sub(r"[.,-]", "", state["latest_message"]["text"]) or []

			compared_prices = ComparePrices.compare_prices(medicine_name)

			message = ''
			if compared_prices:
				message += f"\nI found the following medicines in your prescription"
				for d in compared_prices:
					message += f"\n {d} = {compared_prices[d]}"
			else:
				message += (
					"\nI'm sorry, I couldn't find any medicines in your prescription. Please enter manually."
				)

			dispatcher.utter_message(message)
			# Set all slots to None
			slots = []
			for slot_name in tracker.slots.keys():
				slots.append(SlotSet(slot_name, None))

			return slots

