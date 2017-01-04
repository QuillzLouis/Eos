#    Copyright © 2017  RunasSudo (Yingtong Li)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

try:
	__pragma__('opov')
	IS_PYTHON = False
except Exception:
	IS_PYTHON = True

if IS_PYTHON:
	import random
	system_random = random.SystemRandom()
	
	class BigInt:
		__field_type__ = 'TextField'
		
		def __init__(self, a, b=None):
			if isinstance(a, str):
				if b is None:
					b = 10
				self.impl = int(a, b)
			elif isinstance(a, int):
				self.impl = int(a)
			else:
				raise Exception('Unsupported type passed to BigInt()')
		
		def __str__(self):
			return str(self.impl)
		
		def __int__(self):
			return self.impl
		
		def __eq__(self, other):
			if isinstance(other, BigInt):
				other = other.impl
			return self.impl == other
		
		def __pow__(self, other, modulo=None):
			if isinstance(other, BigInt):
				other = other.impl
			if modulo is None:
				return self.impl.__pow__(other)
			if isinstance(modulo, BigInt):
				modulo = modulo.impl
			return BigInt(self.impl.__pow__(other, modulo))
		
		@staticmethod
		def noncrypto_random(lower_bound, upper_bound):
			return BigInt(random.randint(int(lower_bound), int(upper_bound)))
		
		@staticmethod
		def crypto_random(lower_bound, upper_bound):
			return BigInt(system_random.randint(int(lower_bound), int(upper_bound)))
		
		
		@staticmethod
		def to_python(value):
			return BigInt(value)
		
		@staticmethod
		def from_python(value):
			return str(value.impl)
	
	# Basic arithmetic operators
	for key in ['__sub__', '__mul__', '__mod__']:
		def wrapper(self, other, key=key):
			if isinstance(other, BigInt):
				other = other.impl
			return BigInt(getattr(self.impl, key)(other))
		setattr(BigInt, key, wrapper)
else:
	class BigInt:
		def __init__(self, a, b=None):
			if isinstance(a, str):
				self.impl = nbi()
				self.impl.fromString(a, b)
			elif isinstance(a, int):
				self.impl = nbv(a)
			elif type(a) is not None and hasattr(a, '__proto__') and a.__proto__ == BigInteger.prototype:
				self.impl = a
			else:
				console.error('Unsupported type passed to BigInt()')
				raise Exception()
			
			# Basic arithmetic operators
			# TNYI: Transcrypt drops the self parameter to wrapper for some strange reason, so we must define these at the instance level
			for key, func in [('__add__', 'add'), ('__sub__', 'subtract'), ('__mul__', 'multiply'), ('__mod__', 'mod'), ('__or__', 'or')]:
				# TNYI: No support for the cheaty way we used above
				def makeWrapper(func_):
					def wrapper(other):
						if not isinstance(other, BigInt):
							other = BigInt(other)
						# TNYI: We must explicitly bind() this function
						return BigInt((getattr(self.impl, func_).bind(self.impl))(other.impl))
					return wrapper
				setattr(self, key, makeWrapper(func))
		
		def __str__(self):
			return str(self.impl)
		
		# Frustratingly, transcrypt doesn't like the way we do it above
		def __eq__(self, other):
			if not isinstance(other, BigInt):
				other = BigInt(other)
			return self.impl.compareTo(other.impl) == 0
		def __lt__(self, other):
			if not isinstance(other, BigInt):
				other = BigInt(other)
			return self.impl.compareTo(other.impl) < 0
		
		def __pow__(self, other, modulo=None):
			if not isinstance(other, BigInt):
				other = BigInt(other)
			if modulo is None:
				return BigInt(self.impl.pow(other.impl))
			if not isinstance(modulo, BigInt):
				modulo = BigInt(modulo)
			return BigInt(self.impl.modPow(other.impl, modulo.impl))
		def __lshift__(self, other):
			if isinstance(other, BigInt):
				other = other.impl
			return BigInt(self.impl.shiftLeft(other))
		
		@staticmethod
		def noncrypto_random(lower_bound, upper_bound):
			if not isinstance(lower_bound, BigInt):
				lower_bound = BigInt(lower_bound)
			if not isinstance(upper_bound, BigInt):
				upper_bound = BigInt(upper_bound)
			
			import random
			
			bound_range = upper_bound - lower_bound + 1
			bound_range_bits = bound_range.impl.bitLength()
			
			# Generate a sufficiently large number; work 32 bits at a time
			current_range = 0
			max_int = 2 ** 32 - 1
			big_number = BigInt.ZERO
			while current_range < bound_range_bits:
				random_number = BigInt(random.randint(0, max_int))
				#big_number = (big_number << 32) | random_number
				big_number = big_number.__lshift__(32).__or__(random_number) # TNYI: No << or | support
				current_range = current_range + 32
			
			# Since this is the non-crypto version, just do it modulo
			return lower_bound + (big_number % bound_range)
		
		@staticmethod
		def crypto_random(*args):
			# TODO: Implement this
			return BigInt.noncrypto_random(*args)

BigInt.ZERO = BigInt('0')
BigInt.ONE = BigInt('1')
BigInt.TWO = BigInt('2')
