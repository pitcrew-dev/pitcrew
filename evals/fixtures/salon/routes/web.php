<?php

use Illuminate\Support\Facades\Route;

Route::view("/", "home");
Route::get("/book", [App\Http\Controllers\BookingController::class, "create"]);
