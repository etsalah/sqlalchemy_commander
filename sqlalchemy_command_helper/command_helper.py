#!/usr/bin/env python
"""This module contains code that helps generates the necessary queries that
modify data in the database"""
from datetime import datetime
from typing import Dict, List, TypeVar, Any, Iterable

from sqlalchemy.orm import Session
from sqlalchemy.orm import exc as orm_exc


SessionType = TypeVar('SessionType', bound=Session)


def save(
        session_obj: SessionType, model_cls, fields: Iterable[str],
        data: Dict):
    """This function is responsible for storing a new instance of the model into
    the database

    Arg(s):
    -------
    session_obj -> object used to interact with the database
    model_cls -> class that represents the model that need to be saved in to
        the database
    fields(iterable[str]) -> list of fields that will be set on the model object
        saved to the database
    data (Dict) -> Dictionary that contains the fields (columns) and values that
        need to be set on the model before saving the model instance into the
        database

    Return(s):
    ----------
    returns either a dictionary or instance of the model_cls depending on the
    value of json_result
    """
    obj = model_cls()
    for field in fields:
        if field in data:
            setattr(obj, field, data[field])

    session_obj.add(obj)
    return obj


def update_by_id(
        session_obj, model_cls, find_func, fields: Iterable[str], _id: Any,
        data: Dict):

    """This function is responsible for updating a particular instance of a
    model when the id of that instance is known

    Arg(s)
    ------
    session_obj -> object used to interact with the database
    model_cls -> class that represents the model whose instance needs to be
        updated
    find_func -> function that is called to find the details of object that
        needs to be updated
    fields (Iterable[str]) -> list of fields that can be updated on the model
        before it's written to the database
    _id -> id of the instance of the model that needs to be updated
    data (dict) -> Dictionary that contains the fields that need to be updated
        and the values that they need to be set to
    Return(s)
    ---------
    returns a raw instance of the model or a dictionary representing the model
    """
    return update_by_params(
        session_obj, model_cls, find_func, fields, [{"id": {"$eq": _id}}], data
    )


def update_by_params(
        session_obj: SessionType, model_cls, find_func, fields: Iterable[str],
        params: List[Dict], data):
    """This function is updates the instance of the model represented by the
    class in model_cls and identified by the arguments in the params parameter

    Arg(s)
    ------
    session_obj: the object used to interact with the database
    model_cls: class representing the model whose instance needs to be updated
    find_func: function that needs to be called to find the details of the model
        that needs to be updated
    fields (Iterable[str]) -> list of fields that can be updated on the model
        before it's written to the database
    params (List[Dict]) -> parameters that will be used to identify the model
        instance that needs to be updated
    data (Dict) -> the fields that need to be updated with the values in the
        parameter

    Return(s)
    ---------
    returns raw instance or dictionary representing the raw instance based on
    json_result's value
    """

    found_obj = find_func(session_obj, model_cls, params)
    if not found_obj:
        raise orm_exc.NoResultFound()

    for field in fields:
        if field in data:
            setattr(found_obj, field, data[field])

    session_obj.add(found_obj)
    return found_obj


def delete_by_id(
        session_obj: SessionType, model_cls, find_func, fields: Iterable[str],
        _id, data: Dict = None):
    """This function is used to update an instance of the class indicated by
    id in _id

    Arg(s)
    ------
    session_obj -> object used to interact with the database
    model_cls -> class representing the model that needs to be updated
    find_func -> function that needs to be called to find the details of the
        model that needs to be updated
    fields (Iterable[str]) -> list of fields that can be updated on the model
        before it's written to the database
    _id -> id of the instance of the class that needs to be deleted
    data (Dict) -> other data that needs to be set of the object after it has
        been marked as deleted
    Return(s)
    ---------
    returns raw instance or dictionary representing the raw instance based on
    json_result's value
    """
    return delete_by_params(
        session_obj, model_cls, find_func, fields, [{"id": {"$eq": _id}}], data
    )


def delete_by_params(
        session_obj: SessionType, model_cls, find_func, fields: Iterable[str],
        params: List[Dict], data: Dict = None):
    """This function is used to update an instance of the class indicated by
    parameters in the params argument

    Arg(s)
    ------
    session_obj -> object used to interact with the database
    model_cls -> class representing the model that needs to be updated
    find_func -> function that needs to be called to find the details of the 
        model that needs to be updated
    fields (Iterable[str]) -> list of fields that can be updated on the model
        before it's written to the database
    params (List[Dict]) -> parameters that can be used to identify the instance
        of the model to be deleted
    data (Dict) -> other data that needs to be set of the object after it has
        been marked as deleted
    Return(s)
    ---------
    returns raw instance or dictionary representing the raw instance based on
    json_result's value
    """
    if not data:
        data = {"removed": True, "removed_at": datetime.utcnow()}
    else:
        data.update({"removed": True, "removed_at": datetime.utcnow()})

    return update_by_params(
        session_obj, model_cls, find_func, fields, params, data)
