from copy import deepcopy


class Snapshot(object):
	
	__slots__ = ('_event', '_arg', '_frame',
				 '_filename', '_line', '_caller', 
				 '_locals_key', '_locals_dup', '_locals_ref', '_locals_err', 
				 '_cloned')
	
	def __init__(self, frame, event, arg, clone=True):
		

		self._event    = event
		self._arg      = arg
		self._frame    = frame

		self._filename = frame.f_code.co_filename
		self._line     = frame.f_lineno
		self._caller   = frame.f_code.co_name

		local_key = set()
		local_dup = {}
		local_ref = {}
		local_err = {}

		if clone:
			# attempt to make a deepcopy of each item,
			# note that Java and complex objects will fail deepcopy
			#   and instead will be saved by reference only
			for key,value in frame.f_locals.items():
				try:
					local_dup[key] = deepcopy(value)
				except Exception, err:
					local_ref[key] = value
					local_err[key] = err
		self._cloned = clone
		
		self._locals_key = local_key
		self._locals_dup = local_dup
		self._locals_ref = local_ref
		self._locals_err = local_err


	@property
	def event(self):
		return self._event
	@property
	def arg(self):
		return self._arg
	@property
	def frame(self):
		return self._frame
	@property
	def filename(self):
		return self._filename
	@property
	def line(self):
		return self._line
	@property
	def caller(self):
		return self._caller

	@property
	def cloned(self):
		return self._cloned
	@property
	def local(self):
		return dict(self._local_ref.items() + self._local_dup.items())
	@property
	def local_uncloned(self):
		return self._locals_err.keys()
	

	def __getitem__(self, key):
		"""Get var from frame. Note that this has various guarantees depending on setup.

		If the frame locals were cloned, then it will first try to return the deepcopy
		  version (to avoid mutation as frame evolves), then it'll fall back to a reference.
		If references were not cloned, the frame is directly referenced. Note that f_locals
		  will mutate as the frame executes, so this is the least reliable way to see
		  what is currently happening.
		"""
		if self._cloned:
			val = self._locals_dup.get(key)
			if val is None:
				return self._locals_ref.get(key)
			else:
				return val
		else:
			return self._frame.f_locals[key]


	def as_dict(self):
		props = 'event arg frame filename line caller local'.split()
		return dict((prop,getattr(self,prop)) for prop in props)
