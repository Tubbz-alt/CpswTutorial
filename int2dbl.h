#ifndef CPSW_EXAMPLE_INT2DBL_H
#define CPSW_EXAMPLE_INT2DBL_H

 //@C Copyright Notice
 //@C ================
 //@C This file is part of CPSW. It is subject to the license terms in the LICENSE.txt
 //@C file found in the top-level directory of this distribution and at
 //@C https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html.
 //@C
 //@C No part of CPSW, including this file, may be copied, modified, propagated, or
 //@C distributed except according to the terms contained in the LICENSE.txt file.

#include <cpsw_api_user.h>
#include <cpsw_sval.h>

// create a subclass of IntField which applies
// a linear transformation to convert integers <-> doubles.
//
//  doubleVal = (intVal + intOffset) * scale + offset
//

class CInt2Dbl;
typedef shared_ptr<CInt2Dbl>       Int2Dbl;
typedef shared_ptr<const CInt2Dbl> ConstInt2Dbl;

class CInt2Dbl : public CIntEntryImpl {
private:
	double   scale_;
    double   offset_;
	uint64_t intOffset_;

protected:
	static const uint8_t  FRAC_BITS_DFLT = 16;
	static const double   SCALE_DFLT     = 1.0;
	static const double   OFF_DFLT       = 0.0;
	static const uint64_t INTOFF_DFLT    = 0;

public:
	// constructors -- support only YAML; no c++ builder API

	// constructor (from YAML)
    CInt2Dbl(Key &k, YamlState &n);

	// copy constructor
	CInt2Dbl(const CInt2Dbl &orig, Key &k);

	// every subclass must provide this (polymorphic cloning)
	virtual CInt2Dbl *clone(Key &k) { return new CInt2Dbl( *this, k ); }

	// check validity of construction parameters
	void checkArgs();

	// getters
	double getScale() const
	{
		return scale_;
	}

	double getOffset() const
	{
		return offset_;
	}

	uint64_t getIntOffset() const
	{
		return intOffset_;
	}


	virtual void dumpYamlPart(YAML::Node &n) const;

	// unique name (for class factory)
	static const char *_getClassName()       { return "Int2Dbl";    }

	// every subclass must provide this (polymorphic access to class name)
	virtual const char *getClassName() const { return _getClassName(); }

	// YAML config save/restore -- inherit from CIntEntryImpl
	//virtual YAML::Node dumpMyConfigToYaml(Path p)                 const;
	//virtual void       loadMyConfigFromYaml(Path p, YAML::Node &) const;

	// create an adapter object (which contains run-time state data)
	virtual EntryAdapt createAdapter(IEntryAdapterKey &k, Path, const std::type_info&) const;

};

// Adapters could hold run-time state information;
class CInt2Dbl_ROAdapt: public virtual CScalVal_ROAdapt {
public:
	CInt2Dbl_ROAdapt(Key &k, Path p, ConstInt2Dbl ie);

	virtual void int2dbl(double *dst, uint64_t *src, unsigned n);
};

// Adapters could hold run-time state information;
class CInt2Dbl_WOAdapt: public virtual CScalVal_WOAdapt {
public:
	CInt2Dbl_WOAdapt(Key &k, Path p, ConstInt2Dbl ie);

	virtual void dbl2int(uint64_t *dst, double *src, unsigned n);
};

class CInt2DblAdapt: public virtual CInt2Dbl_ROAdapt, public virtual CInt2Dbl_WOAdapt, public virtual IDoubleVal {
public:
	CInt2DblAdapt(Key &k, Path p, ConstInt2Dbl ie);
};

#endif
